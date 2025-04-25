from core.entities.ball import Ball, BallController
from core.entities.grid import Grid
from core.entities.hollow_box import HollowBox
from core.entities.player import Player, PlayerController

from game_modules import constants

from core.utilities import DrawManager
from core.utilities import JsonConfig
from core.utilities import ResourceManager

import os
import sys

import pygame

import pygame_gui
from pygame_gui import UIManager
from pygame_gui.core import *
from pygame_gui.elements import *

import pymunk
from pymunk import Space
from pymunk import pygame_util

import random

import timer


class PingPY(pygame.Window):
    MAIN_STATE = 0
    PREPARATION_STATE = 1
    THROWING_STATE = 2
    PLAYING_STATE = 3
    END_STATE = 4

    def __init__(self):
        "====----    Initialization     ----===="
        # Inits pygame module
        pygame.init()
        pygame.mixer.init()

        self.clock = pygame.time.Clock() # Defines pygame clock object

        self.json_config = JsonConfig(os.path.abspath("properties.json"))

        self.STATES = {getattr(self, state) : state for state in dir(self) if state.endswith("_STATE")}

        # Inits draw manager
        self.draw_manager = pygame.sprite.Group()

        # Inits resource manager
        if not self.json_config.has("chosen_resource"):
            self.json_config.set("chosen_resource", "default.zip")
        self.resource_manager = ResourceManager(os.path.join(self.get_execpath(), "resources"))
        self.resource_manager.load(self.json_config.get("chosen_resource"))

        # Defines window params
        info = pygame.display.Info()
        if not self.json_config.has("window"):
            self.json_config.set("window.fullscreen", True)
            self.json_config.set("window.resolution", f"{info.current_w}x{info.current_h}")
            self.json_config.set("window.fps_lock", 60)

        # Creates window
        super().__init__("PingPY",
                         size = list(map(int, self.json_config.get("window.resolution").lower().split("x"))),
                         fullscreen = self.json_config.get("window.fullscreen"))
        self.FPS_LOCK = self.json_config.get("window.fps_lock")

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
        self.space = Space()

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
        self.GRID_RECT = pygame.Rect((0, 0), (self.size[0], self.size[1] / 2))
        self.GRID_SIZES = Grid.get_valid_sizes(self.size, constants.Grid.DEFAULT_START, constants.Grid.DEFAULT_STOP + 1)
        self.grid_current_size = 1

        # Defines player vars
        self.PLAYER_DEFAULT_POS = (self.size[0] / 2, self.size[1] - 50 * self.SIZE_FACTOR)

        "====----          GUI          ----===="
        # Defines gui layout
        gui_size = tuple(map(lambda point: point * self.SIZE_FACTOR, constants.Gui.DEFAULT_SIZE))
        gui_spacing = constants.Gui.DEFAULT_SPACING * self.SIZE_FACTOR
        temp_rect = pygame.Rect()

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
        UIButton(temp_rect, "Start", self.ui_manager, self.preparation_container, command = self.start_level,
                 object_id = ObjectID(class_id = "prep.@button", object_id = "prep.#start_button"),
                 anchors = {"right":"right", "bottom":"bottom"})

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

    def reset_level(self, damage_by: int):
        "Returns player and ball to start position, reduces player's health by PLAYER_DEFAULT_DAMAGE"
        self.master.play(self.sounds["player.damage"])
        self.player.move_to_ip(center = self.PLAYER_DEFAULT_POS)
        self.player.damage(damage_by)
        self.ball.move_to_ip(center = self.BALL_DEFAULT_POS)
        self.ball.body.velocity = 0, 0
        self.ball_controller.set_angle(90)
        self.goto("THROWING")

    def start_level(self):
        "Starts new level"
        player_size = list(map(lambda point: point * self.SIZE_FACTOR, constants.Player.DEFAULT_SIZE))
        player_rect = pygame.Rect((0, 0), player_size)
        player_rect.center = (self.size[0] / 2, self.size[1] - 50 * self.SIZE_FACTOR)
        player_surface = pygame.Surface(player_rect.size)
        player_surface.fill((255, 255, 255, 255))
        self.player = Player(player_rect, player_surface, 3, 500)
        self.player_controller = PlayerController(self.player)
        self.player.add(self.space)
        self.draw_manager.add(self.player)

        ball_size = (constants.Ball.DEFAULT_RADIUS * 2 * self.SIZE_FACTOR, ) * 2
        ball_rect = pygame.Rect((0, 0), ball_size)
        ball_rect.center = self.BALL_DEFAULT_POS
        ball_surface = pygame.Surface(ball_rect.size)
        ball_surface.fill((255, 255, 255, 255))
        self.ball = Ball(ball_rect, ball_surface)
        self.ball_controller = BallController(self.ball)
        self.ball.add(self.space)
        self.draw_manager.add(self.ball)

        grid_body_surface = pygame.Surface(player_rect.size)
        grid_body_surface.fill((255, 255, 255, 255))
        self.grid = Grid(self.GRID_RECT, (self.GRID_SIZES[self.grid_current_size], ) * 2, grid_body_surface)
        self.grid.add(self.space)
        self.draw_manager.add(self.grid)

        self.hollow_box = HollowBox(pygame.Rect(-constants.HollowBox.DEFAULT_WIDTH - 1, -constants.HollowBox.DEFAULT_WIDTH - 1,
                                                self.size[0] + constants.HollowBox.DEFAULT_WIDTH * 2 + 1, self.size[1] + 50),
                                    constants.HollowBox.DEFAULT_WIDTH)
        self.hollow_box.add(self.space)

        pygame.mixer.music.pause()
        self.master.play(self.sounds["game.start"])
        self.goto("THROWING")

    def end_level(self, timer_id = None, time = None):
        "Stops current level"
        if timer_id: timer.kill_timer(timer_id)
        self.draw_manager.kill_all()
        pygame.mixer.music.unpause()
        self.goto("MAIN")

    def process_collision(self, arbiter: pymunk.arbiter.Arbiter, space: pymunk.Space, data):
        "Processes collisions between the ball and the grid cell"
        collided_shape = arbiter.shapes[1]
        [self.grid.kill_sprite(sprite) for sprite in self.grid.sprites() if sprite.shape == collided_shape]
        self.master.play(random.choice(self.sounds["ball.jumps"]))
        return True

    def process_controls(self):
        "Processes all keybinds"
        holded_keys = pygame.key.get_pressed()
        pressed_keys = pygame.key.get_just_pressed()

        "====----      Holded keys      ----===="
        if hasattr(self, "player") and hasattr(self, "ball"):
            if holded_keys[pygame.K_a] or holded_keys[pygame.K_LEFT]:
                if self.state == self.THROWING_STATE:
                    self.ball_controller.rotate_left(self.time_delta)

                if self.state == self.PLAYING_STATE and self.player.rect.left > 0:
                    self.player_controller.move_left(self.time_delta)

            elif holded_keys[pygame.K_d] or holded_keys[pygame.K_RIGHT]:
                if self.state == self.THROWING_STATE:
                    self.ball_controller.rotate_right(self.time_delta)

                if self.state == self.PLAYING_STATE and self.player.rect.right < self.size[0]:
                    self.player_controller.move_right(self.time_delta)

        "====----     Pressed keys      ----===="
        if pressed_keys[pygame.K_F3]: self.debug = not self.debug # Toggle debug

        if self.state == self.THROWING_STATE and pressed_keys[pygame.K_SPACE]:
            self.ball_controller.launch(30)
            self.goto("PLAYING")

        if self.state == self.PLAYING_STATE and pressed_keys[pygame.K_q]:
             self.reset_level(constants.Player.DEFAULT_DAMAGE)

        if pressed_keys[pygame.K_ESCAPE]:
            if self.state in [self.THROWING_STATE, self.PLAYING_STATE]: self.end_level()

    def process_events(self):
        "Processes all pygame and pygame_gui events"
        # Getting all pygame events
        for event in pygame.event.get():

            # Adding pygame GUI events to other
            self.ui_manager.process_events(event)

            if event.type == pygame.QUIT: self.running = False

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
            if self.ball.get_position()[1] > self.size[1]:
                self.reset_level(constants.Player.DEFAULT_DAMAGE)

            # Game over when the player's health == 0
            if not self.player.get_health():
                self.end_label.set_text("Game over!")
                timer.set_timer(2000, self.end_level)
                self.master.play(self.sounds["player.die"])
                self.goto("END")

            # Game win when ball breaks all grid bodies
            if not len(self.grid.sprites()):
                self.player_score += (500 * (self.grid_current_size + 1) + self.player.health * 25)
                self.end_label.set_text("You win!")
                timer.set_timer(2000, self.end_level)
                self.master.play(self.sounds["player.win"])
                self.goto("END")

    def process_render(self):
        self.screen.fill((0, 0, 0, 0))

        self.ui_manager.draw_ui(self.screen)
        self.draw_manager.draw(self.screen)

        if self.state == self.PREPARATION_STATE:
            grid_color = self.ui_manager.get_theme().get_colour("normal_text")
            Grid.draw_preview(self.screen, grid_color, self.GRID_RECT, (self.GRID_SIZES[self.grid_current_size], ) * 2)

        elif self.state in [self.THROWING_STATE, self.PLAYING_STATE]:
            if self.state == self.THROWING_STATE:
                self.ball_controller.draw_arrow(self.screen)

    def process_render_debug(self):
        "Renders all values for debugging"
        self.debug_font = pygame.sysfont.SysFont("NotoSans", 20)
        if self.debug:
            if self.state in [self.THROWING_STATE, self.PLAYING_STATE]: self.space.debug_draw(self.options)
            debug_info = [f"{self.fps} ({self.FPS_LOCK}) fps", f"state: {self.STATES[self.state]} ({self.state})"]
            self.screen.blit(self.debug_font.render("\n".join(debug_info), True, (255, 255, 255, 255), (0, 0, 0, 0)), (0, 0))

    def run(self):
        "Runs main cycle"
        self.running = True
        self.goto("MAIN")
        pygame.mixer.music.play(-1)
        while self.running:
            self.time_delta = self.clock.tick(self.FPS_LOCK) / 1000.0
            self.fps = round(self.clock.get_fps())

            if self.state >= self.THROWING_STATE: pygame.mouse.set_visible(False)
            else: pygame.mouse.set_visible(True)

            "====---- Update ----===="
            self.process_events()
            # self.process_player_events()
            self.process_controls()
            self.draw_manager.update()
            self.ui_manager.update(self.time_delta)
            self.space.step(self.time_delta)


            "====----  Draw  ----===="
            self.process_render()
            self.process_render_debug()

            self.flip() # Displaying on window
        pygame.mixer.music.unload()
        pygame.quit()
        self.resource_manager.close()


#Launches the game
if __name__ == "__main__": PingPY().run()