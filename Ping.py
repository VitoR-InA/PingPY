from game_modules.bodies import Ball
from game_modules.bodies import Grid
from game_modules.bodies import HollowBox
from game_modules.bodies import Player

from game_modules.constants import *

from game_modules.utils import JsonConfig
from game_modules.utils import ResourceManager

import os
import sys

import pygame
from pygame import Rect
from pygame import Window

import pygame_gui
from pygame_gui import UIManager
from pygame_gui.core import ObjectID
from pygame_gui.core import UIContainer
from pygame_gui.elements import UIButton, UILabel, UIHorizontalSlider, UIPanel

import pymunk
from pymunk import pygame_util

import random

import timer


class PingPY(Window):
    MAIN_STATE = 0
    SHOP_STATE = 1
    PREPARATION_STATE = 2
    THROWING_STATE = 3
    PLAYING_STATE = 4
    END_STATE = 5

    def __init__(self):
        "====----    Initialization     ----===="
        # Inits pygame module
        pygame.init()
        pygame.mixer.init()

        self.clock = pygame.time.Clock() # Defines pygame clock object

        self.json_config = JsonConfig("properties.json")

        self.STATES = {getattr(self, state) : state for state in dir(self) if state.endswith("_STATE")}

        # Inits resource manager
        if not self.json_config.has(section = None, key = "chosen_resource"): self.json_config.set(section = None, key_value = (("chosen_resource", "default.zip"), ))
        self.resource_manager = ResourceManager(os.path.join(self.get_execpath(), "resources"))
        self.resource_manager.load(self.json_config.get(section = None, key = "chosen_resource"))

        # Defines window measures
        info = pygame.display.Info()
        if not self.json_config.has(section = "window", key = None): self.json_config.set(section = "window", key_value = (("fullscreen", True),
                                                                               ("resolution", "x".join(map(str, [info.current_w, info.current_h])))))

        # Creates window
        super().__init__("PingPY",
                         size = list(map(int, self.json_config.get(section = "window", key = "resolution").split("x"))),
                         fullscreen = self.json_config.get(section = "window", key = "fullscreen"))

        self.SIZE_FACTOR = (self.size[0] / 1920 / 2) + (self.size[1] / 1080 / 2) # Defines coefficient between current monitor size and 1920x1080

        "====----    Pygame surfaces    ----===="
        self.screen = self.get_surface() # Defines window surface

        self.ui_manager = UIManager(self.size, self.resource_manager.get("ui_theme.json")) # Defines UIManager surface

        "====----        Sounds         ----===="
        self.master = pygame.mixer.Channel(0) # Creates pygame master sound channel

        self.sounds = {} # Defines sounds var where all sound will be loaded

        # Loads ball sounds
        self.sounds["ball.jumps"] = [pygame.Sound(os.path.join(self.resource_manager.loaded_resource, "sounds\\ball", path))
                                     for path in os.listdir(self.resource_manager.get("sounds\\ball"))]

        # Loads player sounds
        self.sounds["player.damage"] = pygame.Sound(self.resource_manager.get("sounds\\player\\damage.wav"))
        self.sounds["player.die"] = pygame.Sound(self.resource_manager.get("sounds\\player\\die.wav"))
        self.sounds["player.win"] = pygame.Sound(self.resource_manager.get("sounds\\player\\win.wav"))

        self.sounds["game.start"] = pygame.Sound(self.resource_manager.get("sounds\\game\\start.wav")) # Loads game sounds

        pygame.mixer.music.load(self.resource_manager.get("sounds\\game\\music.wav")) # Loads game music

        "====----      Pymunk init      ----===="
        # Pymunk space setup
        pygame_util.positive_y_is_up = False
        self.space = pymunk.Space()

        # Defines collision handler
        collision_handler = self.space.add_collision_handler(1, 2)
        collision_handler.begin = self.process_collision

        # Defines debug draw options
        self.options = pygame_util.DrawOptions(self.screen)
        self.debug = False

        "====----       Game vars       ----===="
        # Defines ball vars
        self.BALL_DEFAULT_POS = (self.size[0] / 2, self.size[1] - 100 * self.SIZE_FACTOR)

        # Defines grid vars
        self.GRID_RECT = Rect((0, 0), (self.size[0], self.size[1] / 2))
        self.GRID_SIZES = Grid.get_valid_sizes(self.size, GRID_DEFAULT_START, GRID_DEFAULT_STOP + 1)
        self.grid_current_size = 1

        # Defines player vars
        self.PLAYER_DEFAULT_POS = (self.size[0] / 2, self.size[1] - 50 * self.SIZE_FACTOR)
        self.player_score = PLAYER_DEFAULT_SCORE

        # Defines hollow box
        hollow_box = HollowBox(Rect(-HOLLOW_BOX_DEFAULT_WIDTH - 1, -HOLLOW_BOX_DEFAULT_WIDTH - 1,
                                    self.size[0] + HOLLOW_BOX_DEFAULT_WIDTH * 2 + 1, self.size[1] + 50),
                               HOLLOW_BOX_DEFAULT_WIDTH)
        self.space.add(hollow_box, *hollow_box.segments)

        "====----          GUI          ----===="
        # Defines gui layout
        gui_size = tuple(map(lambda point: point * self.SIZE_FACTOR, GAME_DEFAULT_GUI_SIZE))
        gui_spacing = GAME_DEFAULT_GUI_SPACING * self.SIZE_FACTOR
        temp_rect = Rect()

        # Creates containers for all state vars
        for state in self.STATES.values():
            setattr(self, f"{state.removesuffix('_STATE').lower()}_container", UIContainer(self.screen.get_rect(), self.ui_manager))
            UIPanel(self.screen.get_rect(), manager = self.ui_manager, container = getattr(self, f"{state.removesuffix('_STATE').lower()}_container"),
                object_id = ObjectID(class_id = "game.@background_panel", object_id = f"{state.removesuffix('_STATE').lower()}.#background_panel")).change_layer(0)

        "====----    Main container     ----===="
        # Defines game label
        UILabel(self.screen.get_rect(), self.title, self.ui_manager, self.main_container,
                object_id = ObjectID(object_id = "main.#label")).change_layer(1)

        # Defines volume slider
        temp_rect.size = gui_size
        temp_rect.bottomleft = (gui_spacing, -gui_spacing)
        self.volume_sldr = UIHorizontalSlider(temp_rect, 100, (0, 100), self.ui_manager, self.main_container,
                                              object_id = ObjectID(class_id = "main.@slider", object_id = "main.#volume_slider"),
                                              anchors = {"left":"left", "bottom":"bottom"})
        # Defines volume slider label
        UILabel(temp_rect, "Volume", self.ui_manager, self.main_container,
                object_id = ObjectID(class_id = "main.@slider.#label", object_id = "main.#volume_slider.#label"),
                anchors = {"left":"left", "bottom":"bottom"}).change_layer(3)

        # Defines play button
        temp_rect.bottomright = (-gui_spacing, -(gui_spacing * 3 + gui_size[1] * 2))
        UIButton(temp_rect, "Play", self.ui_manager, self.main_container, command = lambda: self.goto("PREPARATION"),
                 object_id = ObjectID(class_id = "main.@button", object_id = "main.#play_button"),
                 anchors = {"right":"right", "bottom":"bottom"})

        # Defines shop button
        temp_rect.bottomright = (-gui_spacing, -(gui_spacing * 2 + gui_size[1]))
        UIButton(temp_rect, "Shop", self.ui_manager, self.main_container, command = lambda: self.goto("SHOP"),
                 object_id = ObjectID(class_id = "main.@button", object_id = "main.#shop_button"),
                 anchors = {"right":"right", "bottom":"bottom"})

        # Defines exit button
        temp_rect.bottomright = (-gui_spacing, -gui_spacing)
        UIButton(temp_rect, "Exit", self.ui_manager, self.main_container, command = lambda: pygame.event.post(pygame.Event(pygame.QUIT)),
                 object_id = ObjectID(class_id = "main.@button", object_id = "main.#exit_button"),
                 anchors = {"right":"right", "bottom":"bottom"})

        "====---- Preparation container ----===="
        # Defines preparation back button
        temp_rect.size = (gui_size[1], ) * 2
        temp_rect.bottomleft = (gui_spacing, -gui_spacing)
        UIButton(temp_rect, "Back", self.ui_manager, self.preparation_container, command = lambda: self.goto("MAIN"),
                 object_id = ObjectID(class_id = "game.@back_button", object_id = "prep.#back_button"),
                 anchors = {"left":"left", "bottom":"bottom"})

        # Defines grid size slider
        temp_rect.size = gui_size
        temp_rect.bottomleft = (gui_spacing * 2 + gui_size[1], -gui_spacing)
        self.size_sldr = UIHorizontalSlider(temp_rect, 1, (0, 2), self.ui_manager, self.preparation_container,
                                            object_id = ObjectID(class_id = "prep.@slider", object_id = "prep.#size_slider"),
                                            anchors = {"bottom":"bottom"})

        # Defines grid size slider label
        UILabel(temp_rect, "Size", self.ui_manager, self.preparation_container,
                object_id = ObjectID(class_id = "prep.@slider.#label", object_id = "prep.#size_slider.#label"),
                anchors = {"left":"left", "bottom":"bottom"}).change_layer(3)

        # Defines start button
        temp_rect.bottomright = (-gui_spacing, -gui_spacing)
        UIButton(temp_rect, "Start", self.ui_manager, self.preparation_container, command = self.new_level,
                 object_id = ObjectID(class_id = "prep.@button", object_id = "prep.#start_button"),
                 anchors = {"right":"right", "bottom":"bottom"})

        "====----    Shop container     ----===="
        # Defines shop label
        UILabel(self.screen.get_rect(), "Shop", self.ui_manager, self.shop_container,
                object_id = ObjectID(object_id = "shop.#label")).change_layer(1)

        temp_rect.size = gui_size
        temp_rect.topright = (-gui_spacing, gui_spacing)
        UIPanel(temp_rect, manager = self.ui_manager, container = self.shop_container,
                object_id = ObjectID(object_id = "shop.#score_panel"),
                anchors = {"right":"right", "top":"top"})

        self.player_score_lbl = UILabel(temp_rect, "Score", self.ui_manager, self.shop_container,
                                        object_id = ObjectID(object_id = "shop.#score_panel.#label"),
                                        anchors = {"right":"right", "top":"top"})

        # Defines shop back button
        temp_rect.size = (gui_size[1], ) * 2
        temp_rect.bottomleft = (gui_spacing, -gui_spacing)
        UIButton(temp_rect, "Back", self.ui_manager, self.shop_container, command = lambda: self.goto("MAIN"),
                 object_id = ObjectID(class_id = "game.@back_button", object_id = "shop.#back_button"),
                 anchors = {"left":"left", "bottom":"bottom"})

        # Defines player speed upgrade
        temp_rect.size = gui_size
        temp_rect.bottomright = (-gui_spacing, -gui_spacing)
        UIPanel(temp_rect, manager = self.ui_manager, container = self.shop_container,
                object_id = ObjectID(class_id = "shop.@panel.#label", object_id = "shop.#speed_panel.#label"),
                anchors = {"centerx":"centerx", "bottom":"bottom"})
        self.player_speed_lbl = UILabel(temp_rect, "Speed", self.ui_manager, self.shop_container,
                                        object_id = ObjectID(class_id = "shop.@panel.#label", object_id = "shop.#speed_panel.#label"),
                                        anchors = {"centerx":"centerx", "bottom":"bottom"})

        # Defines player health upgrade
        temp_rect.size = gui_size
        temp_rect.bottomleft = (gui_size[0] + gui_spacing, -gui_spacing)
        UIPanel(temp_rect, manager = self.ui_manager, container = self.shop_container,
                object_id = ObjectID(class_id = "shop.@panel", object_id = "shop.#health_panel"),
                anchors = {"centerx":"centerx", "bottom":"bottom"})
        self.player_health_lbl = UILabel(temp_rect, "Health", self.ui_manager, self.shop_container,
                                         object_id = ObjectID(class_id = "shop.@panel.#label", object_id = "shop.#health_panel.#label"),
                                         anchors = {"centerx":"centerx", "bottom":"bottom"})

        # RIGHT TARGET ISSUE: https://github.com/MyreMylar/pygame_gui/issues/671
        temp_rect.size = (gui_size[1], ) * 2

        temp_rect.bottomright = (-gui_size[0] - gui_spacing, -gui_spacing)
        self.player_speed_minus = UIButton(temp_rect, "-", self.ui_manager, self.shop_container, "Speed -50\nScore +125\nMIN: 500",
                                           object_id = ObjectID(object_id = "shop.#minus_button"),
                                           anchors = {"left_target":self.player_speed_lbl, "bottom":"bottom"})

        self.player_health_minus = UIButton(temp_rect, "-", self.ui_manager, self.shop_container, "Health -1\nScore +250\nMIN: 3",
                                            object_id = ObjectID(object_id = "shop.#minus_button"),
                                            anchors = {"left_target":self.player_health_lbl, "bottom":"bottom"})

        temp_rect.bottomleft = (gui_spacing, -gui_spacing)
        self.player_speed_plus = UIButton(temp_rect, "+", self.ui_manager, self.shop_container, "Speed +50\nScore -250\nMAX: 1000",
                                          object_id = ObjectID(object_id = "shop.#plus_button"),
                                          anchors = {"left_target":self.player_speed_lbl, "bottom":"bottom"})

        self.player_health_plus = UIButton(temp_rect, "+", self.ui_manager, self.shop_container, "Health +1\nScore -500\nMAX: 5",
                                           object_id = ObjectID(object_id = "shop.#plus_button"),
                                           anchors = {"left_target":self.player_health_lbl, "bottom":"bottom"})

        "====----     End container     ----===="
        self.end_label = UILabel(self.screen.get_rect(), "", self.ui_manager, self.end_container,
                                 object_id = ObjectID(object_id = "end.#label"))

    @classmethod
    def get_execpath(self):
        if hasattr(sys, "frozen"): return os.path.dirname(sys.executable)
        else: return os.path.dirname(os.path.abspath(__file__))

    def goto(self, state: str):
        """
        Sets the value of self.state to the value given in the state argument, showing the corresponding container if it exists.

        :param state: The name of the state and container at once
        """
        self.state = list(self.STATES.keys())[list(self.STATES.values()).index(f"{state.upper()}_STATE")]
        for container_name in [attr for attr in dir(self) if attr.endswith("_container")]:
            container: UIContainer = getattr(self, container_name)
            if container_name.startswith(state.lower()): container.show()
            else: container.hide()

    def reset_player(self, damage: int):
        "Returns player and ball to start position, reduces player's health by PLAYER_DEFAULT_DAMAGE"
        self.master.play(self.sounds["player.damage"])
        self.player.take_damage(damage)
        self.player.set_position(self.PLAYER_DEFAULT_POS)
        self.ball.set_position(self.BALL_DEFAULT_POS)
        self.ball.set_angle(90)
        self.goto("THROWING")

    def new_level(self):
        "Starts new level"
        PLAYER_SIZE = list(map(lambda point: point * self.SIZE_FACTOR, PLAYER_DEFAULT_SIZE))
        self.player = Player(Rect(self.PLAYER_DEFAULT_POS, PLAYER_SIZE))
        self.space.add(self.player, self.player.shape)

        self.ball = Ball(BALL_DEFAULT_COLOR, self.BALL_DEFAULT_POS, BALL_DEFAULT_RADIUS * self.SIZE_FACTOR)
        self.space.add(self.ball, self.ball.shape)

        self.grid = Grid(self.GRID_RECT, (self.GRID_SIZES[self.grid_current_size], ) * 2)
        self.space.add(*self.grid.bodies, *self.grid.shapes)

        pygame.mixer.music.pause()
        self.master.play(self.sounds["game.start"])
        self.goto("THROWING")

    def end_level(self, timer_id = None, time = None):
        "Stops current level"
        if timer_id: timer.kill_timer(timer_id)
        self.grid.clear()
        self.space.remove(self.player, self.player.shape)
        self.space.remove(self.ball, self.ball.shape)
        pygame.mixer.music.unpause()
        self.goto("MAIN")

    def process_collision(self, arbiter: pymunk.arbiter.Arbiter, space: pymunk.Space, data):
        "Processes collisions between the ball and the grid body"
        collided_shape = arbiter.shapes[1]
        space.remove(collided_shape.body, collided_shape)
        self.grid.remove(collided_shape.body, collided_shape)
        self.master.play(random.choice(self.sounds["ball.jumps"]))
        self.player_score += 5
        return True

    def process_controls(self):
        "Processes all keybinds"
        holded_keys = pygame.key.get_pressed()
        pressed_keys = pygame.key.get_just_pressed()

        "====----      Holded keys      ----===="
        if hasattr(self, "player") and hasattr(self, "ball"):
            if holded_keys[pygame.K_a] or holded_keys[pygame.K_LEFT]:
                if self.state == self.THROWING_STATE and self.ball.arrow_angle < 135:
                    self.ball.arrow_angle += 100 * self.time_delta

                if self.state == self.PLAYING_STATE and self.player.rect.left > 0:
                    self.player.velocity = (-self.player.speed * self.SIZE_FACTOR, 0)

                else: self.player.velocity = (0, 0)

            elif holded_keys[pygame.K_d] or holded_keys[pygame.K_RIGHT]:
                if self.state == self.THROWING_STATE and self.ball.arrow_angle > 45:
                    self.ball.arrow_angle -= 100 * self.time_delta

                if self.state == self.PLAYING_STATE and self.player.rect.right < self.size[0]:
                    self.player.velocity = (self.player.speed * self.SIZE_FACTOR, 0)

                else: self.player.velocity = (0, 0)

            else: self.player.velocity = (0, 0)

        "====----     Pressed keys      ----===="
        if pressed_keys[pygame.K_F3]: self.debug = not self.debug # Toggle debug

        if self.state == self.THROWING_STATE and pressed_keys[pygame.K_SPACE]: self.goto("PLAYING")

        if self.state == self.PLAYING_STATE and pressed_keys[pygame.K_q]:
             self.reset_player(PLAYER_DEFAULT_DAMAGE)

        if pressed_keys[pygame.K_ESCAPE]:
            if self.state in [self.THROWING_STATE, self.PLAYING_STATE]: self.end_level()
            elif self.state in [self.SHOP_STATE, self.PREPARATION_STATE]: self.goto("MAIN")

    def process_events(self):
        "Processes all pygame and pygame_gui events"
        # Getting all pygame events
        for event in pygame.event.get():

            # Adding pygame GUI events to other
            self.ui_manager.process_events(event)

            if event.type == pygame.QUIT: self.running = False

            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                # Speed upgrade
                if event.ui_element == self.player_speed_minus and Player.speed > 500:
                    self.player_score += 125
                    Player.speed -= 50

                if event.ui_element == self.player_speed_plus and self.player_score >= 250 and Player.speed < 1000:
                    self.player_score -= 250
                    Player.speed += 50

                # Health upgrade
                if event.ui_element == self.player_health_minus and Player.max_health > 3:
                    self.player_score += 250
                    Player.max_health -= 1

                if event.ui_element == self.player_health_plus and self.player_score >= 500 and Player.max_health < 10:
                    self.player_score -= 500
                    Player.max_health += 1

            "====---- Slider event ----===="
            if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                if event.ui_element == self.volume_sldr:
                    pygame.mixer.music.set_volume(event.value / 100)
                    self.master.set_volume(event.value / 100)

                if event.ui_element == self.size_sldr:
                    self.grid_current_size = event.value

    def process_player_events(self):
        "Processes player events. Such as winning, losing, and taking damage."
        if self.state in [self.THROWING_STATE, self.PLAYING_STATE]:
            # Decrease player's health by 1
            if self.ball.position[1] > self.size[1]:
                self.reset_player(PLAYER_DEFAULT_DAMAGE)

            # Game over when the player's health == 0
            if not self.player.health:
                self.end_label.set_text("Game over!")
                timer.set_timer(2000, self.end_level)
                self.master.play(self.sounds["player.die"])
                self.goto("END")

            # Game win when ball breaks all grid bodies
            if not len(self.grid.shapes):
                self.player_score += (500 * (self.grid_current_size + 1) + self.player.health * 25)
                self.end_label.set_text("You win!")
                timer.set_timer(2000, self.end_level)
                self.master.play(self.sounds["player.win"])
                self.goto("END")

    def process_render(self):
        self.screen.fill("#000000")

        self.ui_manager.draw_ui(self.screen)

        if self.state == self.SHOP_STATE:
            self.player_score_lbl.set_text(f"Score: {self.player_score}")
            self.player_speed_lbl.set_text(f"Speed: {Player.speed}")
            self.player_health_lbl.set_text(f"Health: {Player.max_health}")

        elif self.state == self.PREPARATION_STATE: Grid.draw_preview(self.screen, self.ui_manager.get_theme().get_colour("noraml_text"),
                                                                self.GRID_RECT, (self.GRID_SIZES[self.grid_current_size], ) * 2)

        elif self.state in [self.THROWING_STATE, self.PLAYING_STATE]:
            if self.state == self.THROWING_STATE:
                self.ball.draw_arrow(self.screen)
            self.player.draw(self.screen)
            self.ball.draw(self.screen)
            self.grid.draw(self.screen)

    def process_render_debug(self):
        "Renders all values for debugging"
        self.debug_font = pygame.sysfont.SysFont("NotoSans", 20)
        if self.debug:
            if self.state in [self.THROWING_STATE, self.PLAYING_STATE]: self.space.debug_draw(self.options)
            debug_info = [f"{self.fps} ({GAME_FPS_LOCK}) fps", f"state: {self.STATES[self.state]} ({self.state})"]
            self.screen.blit(self.debug_font.render("\n".join(debug_info), True, "#FFFFFF", "#000000"), (0, 0))

    def run(self):
        "Runs main cycle"
        self.running = True
        self.goto("MAIN")
        pygame.mixer.music.play(-1)
        while self.running:
            self.time_delta = self.clock.tick(GAME_FPS_LOCK) / 1000.0
            self.fps = round(self.clock.get_fps())

            if self.state >= self.THROWING_STATE: pygame.mouse.set_visible(False)
            else: pygame.mouse.set_visible(True)

            "====---- Update ----===="
            self.process_events()
            self.process_player_events()
            self.process_controls()
            self.ui_manager.update(self.time_delta)
            if self.state == self.PLAYING_STATE: self.space.step(self.time_delta)

            "====----  Draw  ----===="
            self.process_render()
            self.process_render_debug()

            self.flip() # Displaying on window
        pygame.mixer.music.unload()
        pygame.quit()
        self.resource_manager.close()


#Launches the game
if __name__ == "__main__": PingPY().run()