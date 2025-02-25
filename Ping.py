from _internal.game_modules.bodies import Ball
from _internal.game_modules.bodies import HollowBox
from _internal.game_modules.bodies import Player

from _internal.game_modules.constants import *

from _internal.game_modules.grid import Grid

from _internal.game_modules.resource_manager import ResourceManager

import os
import sys

import pygame
from pygame import Rect
from pygame import Window

import pygame_gui
from pygame_gui.core import ObjectID
from pygame_gui import UIManager
from pygame_gui.core import UIContainer
from pygame_gui.elements import UIButton, UILabel, UIHorizontalSlider, UIPanel

import pymunk
from pymunk import pygame_util

from random import randint

import timer


class PingPY(Window):
    def __init__(self):
        "====----      Pygame init      ----===="
        # Pygame init
        pygame.init()
        pygame.mixer.init()

        super().__init__("PingPY", fullscreen_desktop = True)
        self.workpath = self.get_workpath()

        # Defining window vars
        self.clock = pygame.time.Clock()

        self.size_factor = (self.size[0] / 1920 / 2) + (self.size[1] / 1080 / 2)

        "====----    Pygame surfaces    ----===="
        # Main window surface
        self.screen = self.get_surface()

        # UIManager surface
        self.ui_manager = UIManager(self.size)

        "====----        Sounds         ----===="
        # Master pygame channel
        self.master = pygame.mixer.Channel(0)

        # Sounds var
        self.sounds = {}

        # Ball sounds
        self.sounds["jump1"] = pygame.mixer.Sound("_internal\\sounds\\ball\\jump1.wav")
        self.sounds["jump2"] = pygame.mixer.Sound("_internal\\sounds\\ball\\jump2.wav")

        # Player sounds
        self.sounds["player_damage"] = pygame.mixer.Sound("_internal\\sounds\\player\\damage.wav")
        self.sounds["player_die"] = pygame.mixer.Sound("_internal\\sounds\\player\\die.wav")
        self.sounds["player_win"] = pygame.mixer.Sound("_internal\\sounds\\player\\win.wav")

        # Game sounds
        self.sounds["game_start"] = pygame.mixer.Sound("_internal\\sounds\\game\\start.wav")

        # Game music
        pygame.mixer.music.load("_internal\\sounds\\music.wav")

        "====----      Pymunk init      ----===="
        # Pymunk space setup
        pygame_util.positive_y_is_up = False
        self.space = pymunk.Space()

        # Defining on collision handler
        collision_handler = self.space.add_collision_handler(1, 2)
        collision_handler.begin = self.process_collision

        # Defining debug draw options
        self.options = pygame_util.DrawOptions(self.screen)
        self.debug = False

        "====----       Game vars       ----===="
        # Defining ball vars
        self.ball_color = BALL_DEFAULT_COLOR
        self.ball_radius = BALL_DEFAULT_RADIUS
        self.ball_pos = (self.size[0] / 2, self.size[1] - 100 * self.size_factor)

        # Defining grid vars
        self.grid_sizes = Grid.get_valid_sizes(self.size, GRID_DEFAULT_START, GRID_DEFAULT_STOP + 1)
        self.grid_current_size = 1

        # Defining player vars
        self.player_health = PLAYER_DEFAULT_HEALTH
        self.player_score = PLAYER_DEFAULT_SCORE
        self.player_size = PLAYER_DEFAULT_SIZE
        self.player_speed = PLAYER_DEFAULT_SPEED
        self.player_pos = (self.size[0] / 2, self.size[1] - 50 * self.size_factor)

        # Defining walls
        HollowBox(Rect(-WALL_DEFAULT_WIDTH - 1, -WALL_DEFAULT_WIDTH - 1,
                       self.size[0] + WALL_DEFAULT_WIDTH * 2 + 1, self.size[1] + 50),
                  WALL_DEFAULT_WIDTH, self.space)

        "====----          GUI          ----===="
        # Means default gui element size
        gui_size = (GUI_SIZE[0] * self.size_factor, GUI_SIZE[1] * self.size_factor)
        gui_spacing = GUI_SPACING * self.size_factor
        temp_rect = Rect()

        "====----    Main container     ----===="
        # Defining menu container
        self.main_container = UIContainer(self.screen.get_rect(), manager = self.ui_manager)

        # Defining game label
        UILabel(self.screen.get_rect(), self.title, self.ui_manager, self.main_container,
                object_id = ObjectID(object_id = "main.#label")).change_layer(1)

        # Defining volume slider
        temp_rect.size = gui_size
        temp_rect.bottomleft = (gui_spacing, -gui_spacing)
        self.volume_sldr = UIHorizontalSlider(temp_rect, 100, (0, 100), self.ui_manager, self.main_container,
                                              anchors = {"left":"left", "bottom":"bottom"})
        # Defining volume slider label
        UILabel(temp_rect, "Volume", self.ui_manager, self.main_container,
                anchors = {"left":"left", "bottom":"bottom"}).change_layer(3)

        # Defining play button
        temp_rect.bottomright = (-gui_spacing, -(gui_spacing * 3 + gui_size[1] * 2))
        UIButton(temp_rect, "Play", self.ui_manager, self.main_container, command = lambda: self.goto("PREPARATION"),
                 object_id = ObjectID(class_id = "main.@button", object_id = "main.#play_button"),
                 anchors = {"right":"right", "bottom":"bottom"})

        # Defining shop button
        temp_rect.bottomright = (-gui_spacing, -(gui_spacing * 2 + gui_size[1]))
        UIButton(temp_rect, "Shop", self.ui_manager, self.main_container, command = lambda: self.goto("SHOP"),
                 object_id = ObjectID(class_id = "main.@button", object_id = "main.#shop_button"),
                 anchors = {"right":"right", "bottom":"bottom"})

        # Defining exit button
        temp_rect.bottomright = (-gui_spacing, -gui_spacing)
        UIButton(temp_rect, "Exit", self.ui_manager, self.main_container, command = lambda: pygame.event.post(pygame.Event(pygame.QUIT)),
                 object_id = ObjectID(class_id = "main.@button", object_id = "main.#exit_button"),
                 anchors = {"right":"right", "bottom":"bottom"})

        "====---- Preparation container ----===="
        # Defining preparation container
        self.preparation_container = UIContainer(self.screen.get_rect(), manager = self.ui_manager, visible = False)

        # Defining preparation back button
        temp_rect.size = (gui_size[1], ) * 2
        temp_rect.bottomleft = (gui_spacing, -gui_spacing)
        UIButton(temp_rect, "Back", self.ui_manager, self.preparation_container, command = lambda: self.goto("MAIN"),
                 anchors = {"left":"left", "bottom":"bottom"})

        # Defining grid size slider
        temp_rect.size = gui_size
        temp_rect.bottomleft = (gui_spacing * 2 + gui_size[1], -gui_spacing)
        self.size_sldr = UIHorizontalSlider(temp_rect, 1, (0, 2), self.ui_manager, self.preparation_container,
                                            anchors = {"bottom":"bottom"})
        # Defining grid size slider label
        UILabel(temp_rect, "Size", self.ui_manager, self.preparation_container,
                anchors = {"left":"left", "bottom":"bottom"}).change_layer(3)

        # Defining start button
        temp_rect.bottomright = (-gui_spacing, -gui_spacing)
        UIButton(temp_rect, "Start", self.ui_manager, self.preparation_container, command = self.new_level,
                 anchors = {"right":"right", "bottom":"bottom"})

        "====----    Shop container     ----===="
        # Defining shop container
        self.shop_container = UIContainer(self.screen.get_rect(), manager = self.ui_manager, visible = False)

        # Defining shop label
        UILabel(self.screen.get_rect(), "Shop", self.ui_manager, self.shop_container,
                object_id = ObjectID(object_id = "shop.#label")).change_layer(1)

        # Defining shop back button
        temp_rect.size = (gui_size[1], ) * 2
        temp_rect.bottomleft = (gui_spacing, -gui_spacing)
        UIButton(temp_rect, "Back", self.ui_manager, self.shop_container, command = lambda: self.goto("MAIN"),
                 object_id = ObjectID(class_id = "shop.@button", object_id = "shop.#back_button"),
                 anchors = {"left":"left", "bottom":"bottom"})

        # Defining player speed upgrade
        temp_rect.size = gui_size
        temp_rect.bottomright = (-gui_spacing, -gui_spacing)
        UIPanel(temp_rect, manager = self.ui_manager, container = self.shop_container,
                anchors = {"centerx":"centerx", "bottom":"bottom"})
        self.player_speed_lbl = UILabel(temp_rect, "Speed", self.ui_manager, self.shop_container,
                                        anchors = {"centerx":"centerx", "bottom":"bottom"})

        # Defining player health upgrade
        temp_rect.size = gui_size
        temp_rect.bottomleft = (gui_size[0] + gui_spacing, -gui_spacing)
        UIPanel(temp_rect, manager = self.ui_manager, container = self.shop_container,
                anchors = {"centerx":"centerx", "bottom":"bottom"})
        self.player_health_lbl = UILabel(temp_rect, "Health", self.ui_manager, self.shop_container,
                                         anchors = {"centerx":"centerx", "bottom":"bottom"})

        # LEFT TARGET ISSUE: https://github.com/MyreMylar/pygame_gui/issues/671
        temp_rect.size = (gui_size[1], ) * 2

        temp_rect.bottomright = (-gui_size[0] - gui_spacing, -gui_spacing)
        self.player_speed_minus = UIButton(temp_rect, "-", self.ui_manager, self.shop_container, "Speed -50\nScore +125\nMIN: 500",
                                           object_id = ObjectID(class_id = "shop.@button", object_id = "shop.#minus_button"),
                                           anchors = {"left_target":self.player_speed_lbl, "bottom":"bottom"})

        self.player_health_minus = UIButton(temp_rect, "-", self.ui_manager, self.shop_container, "Health -1\nScore +250\nMIN: 3",
                                            object_id = ObjectID(class_id = "shop.@button", object_id = "shop.#minus_button"),
                                            anchors = {"left_target":self.player_health_lbl, "bottom":"bottom"})

        temp_rect.bottomleft = (gui_spacing, -gui_spacing)
        self.player_speed_plus = UIButton(temp_rect, "+", self.ui_manager, self.shop_container, "Speed +50\nScore -250\nMAX: 1000",
                                          object_id = ObjectID(class_id = "shop.@button", object_id = "shop.#plus_button"),
                                          anchors = {"left_target":self.player_speed_lbl, "bottom":"bottom"})

        self.player_health_plus = UIButton(temp_rect, "+", self.ui_manager, self.shop_container, "Health +1\nScore -500\nMAX: 5",
                                           object_id = ObjectID(class_id = "shop.@button", object_id = "shop.#plus_button"),
                                           anchors = {"left_target":self.player_health_lbl, "bottom":"bottom"})

        "====----    Score container    ----===="
        # Defining score container
        self.score_container = UIContainer(self.screen.get_rect(), manager = self.ui_manager, visible = False)

        temp_rect.size = gui_size
        temp_rect.topright = (-gui_spacing, gui_spacing)
        UIPanel(temp_rect, manager = self.ui_manager, container = self.score_container,
                anchors = {"right":"right", "top":"top"})
        self.player_score_lbl = UILabel(temp_rect, "Score", self.ui_manager, self.score_container,
                                        anchors = {"right":"right", "top":"top"})

        "====----       End label       ----===="
        self.end_label = UILabel(self.screen.get_rect(), "", self.ui_manager, visible = False)

    @classmethod
    def get_workpath(self):
        if hasattr(sys, "frozen"): return sys._MEIPASS
        else: return os.path.join(os.path.abspath(__file__), "_internal")

    @classmethod
    def get_execpath(self):
        "!Not using yet!" #TODO return logger, which will be paired to executable path
        if hasattr(sys, "frozen"): return os.path.dirname(sys.executable)
        else: return os.path.abspath(__file__)

    def goto(self, state: str):
        """
        Sets the value of self.state to the value given in the state argument, showing the corresponding container if it exists.

        :param state: The name of the state and container at once
        """
        self.state = list(STATES.values()).index(f"{state.upper()}_STATE")
        for container_name in [attr for attr in dir(self) if attr.endswith("_container")]:
            container: UIContainer = getattr(self, container_name)
            if container_name.startswith(state.lower()): container.show()
            else: container.hide()

    def reset_player(self, damage: int):
        "Returns player and ball to start position, reduces player's health by PLAYER_DEFAULT_DAMAGE"
        self.master.play(self.sounds["player_damage"])
        self.player.take_damage(damage)
        self.player.set_position(self.player_pos)
        self.ball.set_position(self.ball_pos)
        self.ball.set_angle(90)
        self.goto("THROWING")

    def new_level(self):
        "Starts new level"
        player_size = [point * self.size_factor for point in self.player_size]
        self.player = Player(Rect(self.player_pos, player_size), self.player_health)
        self.space.add(self.player, self.player.shape)

        self.ball = Ball(self.ball_color, self.ball_pos, self.ball_radius * self.size_factor)
        self.space.add(self.ball, self.ball.shape)

        self.grid = Grid(Rect((0, 0), (self.size[0], self.size[1] / 2)), (self.grid_sizes[self.grid_current_size], ) * 2)
        self.space.add(*self.grid.bodies, *self.grid.shapes)

        pygame.mixer.music.pause()
        self.master.play(self.sounds["game_start"])
        self.goto("THROWING")

    def end_level(self, timer_id = None, time = None):
        "Stops current level"
        if timer_id: timer.kill_timer(timer_id)
        self.grid.clear()
        self.space.remove(self.player, self.player.shape)
        self.space.remove(self.ball, self.ball.shape)
        pygame.mixer.music.unpause()
        self.end_label.hide()
        self.goto("MAIN")

    def process_collision(self, arbiter: pymunk.arbiter.Arbiter, space: pymunk.Space, data):
        "Processes collisions between the ball and the grid body"
        collided_shape = arbiter.shapes[1]
        space.remove(collided_shape.body, collided_shape)
        self.grid.remove(collided_shape.body, collided_shape)
        self.master.play(self.sounds[f"jump{randint(1, 2)}"])
        self.player_score += 5
        return True

    def process_controls(self):
        "Processes all keybinds"
        holded_keys = pygame.key.get_pressed()
        pressed_keys = pygame.key.get_just_pressed()

        "====----      Holded keys      ----===="
        if self.state == SHOP_STATE or (holded_keys[pygame.K_TAB] and self.state in [THROWING_STATE, PLAYING_STATE]):
            self.player_score_lbl.set_text(f"Score: {self.player_score}")
            self.score_container.show()
        else: self.score_container.hide()

        if hasattr(self, "player") and hasattr(self, "ball"):
            if holded_keys[pygame.K_a] or holded_keys[pygame.K_LEFT]:
                if self.state == THROWING_STATE and self.ball.arrow_angle < 135:
                    self.ball.arrow_angle += 100 * self.time_delta

                if self.state == PLAYING_STATE and self.player.rect.left > 0:
                    self.player.velocity = (-self.player_speed * self.size_factor, 0)

                else: self.player.velocity = (0, 0)

            elif holded_keys[pygame.K_d] or holded_keys[pygame.K_RIGHT]:
                if self.state == THROWING_STATE and self.ball.arrow_angle > 45:
                    self.ball.arrow_angle -= 100 * self.time_delta

                if self.state == PLAYING_STATE and self.player.rect.right < self.size[0]:
                    self.player.velocity = (self.player_speed * self.size_factor, 0)

                else: self.player.velocity = (0, 0)

            else: self.player.velocity = (0, 0)

        "====----     Pressed keys      ----===="
        if pressed_keys[pygame.K_F3]: self.debug = not self.debug # Toggle debug

        if self.state == THROWING_STATE and pressed_keys[pygame.K_SPACE]:
            self.ball_speed = [vel * 20 for vel in self.ball_start_velocity]
            self.ball.velocity = self.ball_speed
            self.state = PLAYING_STATE

        if self.state == PLAYING_STATE and pressed_keys[pygame.K_q]:
             self.reset_player(PLAYER_DEFAULT_DAMAGE)

        if pressed_keys[pygame.K_ESCAPE]:
            if self.state in [THROWING_STATE, PLAYING_STATE]: self.end_level()
            elif self.state in [SHOP_STATE, PREPARATION_STATE]: self.goto("MAIN")


    def process_events(self):
        "Processes all pygame and pygame_gui events"
        # Getting all pygame events
        for event in pygame.event.get():

            # Adding pygame GUI events to other
            self.ui_manager.process_events(event)

            if event.type == pygame.QUIT: self.running = False

            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                # Speed upgrade
                if event.ui_element == self.player_speed_minus and self.player_speed > 500:
                    self.player_score += 125
                    self.player_speed -= 50

                if event.ui_element == self.player_speed_plus and self.player_score >= 250 and self.player_speed < 1000:
                    self.player_score -= 250
                    self.player_speed += 50

                # Health upgrade
                if event.ui_element == self.player_health_minus and self.player_health > 3:
                    self.player_score += 250
                    self.player_health -= 1

                if event.ui_element == self.player_health_plus and self.player_score >= 500 and self.player_health < 10:
                    self.player_score -= 500
                    self.player_health += 1

            "====---- Slider event ----===="
            if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                if event.ui_element == self.volume_sldr:
                    pygame.mixer.music.set_volume(event.value / 100)
                    self.master.set_volume(event.value / 100)

                if event.ui_element == self.size_sldr:
                    self.grid_current_size = event.value

    def process_player_events(self):
        "Processes player events. Such as winning, losing, and taking damage."
        if self.state in [THROWING_STATE, PLAYING_STATE]:
            # Decrease player's health by 1
            if self.ball.position[1] > self.size[1]:
                self.reset_player(PLAYER_DEFAULT_DAMAGE)

            # Game over when the player's health == 0
            if not self.player.health:
                self.end_label.set_text("Game over!")
                self.end_label.show()
                timer.set_timer(2000, self.end_level)
                self.master.play(self.sounds["player_die"])
                self.goto("END")

            # Game win when ball breaks all grid bodies
            if not len(self.grid.shapes):
                self.player_score += (500 * (self.grid_current_size + 1) + self.player.health * 25)
                self.end_label.set_text("You win!")
                self.end_label.show()
                timer.set_timer(2000, self.end_level)
                self.master.play(self.sounds["player_win"])
                self.goto("END")

    def process_render(self):
        if self.state == SHOP_STATE:
            self.player_speed_lbl.set_text(f"Speed: {self.player_speed}")
            self.player_health_lbl.set_text(f"Health: {self.player_health}")

        elif self.state == PREPARATION_STATE: Grid.draw_preview(Rect((0, 0), (self.size[0], self.size[1] / 2)),
                                                                (self.grid_sizes[self.grid_current_size], self.grid_sizes[self.grid_current_size]), self.screen)

        elif self.state in [THROWING_STATE, PLAYING_STATE]:
            if self.state == THROWING_STATE:
                self.ball_start_velocity = self.ball.draw_arrow(self.screen)
            self.player.draw(self.screen)
            self.ball.draw(self.screen)
            self.grid.draw(self.screen)

        self.ui_manager.draw_ui(self.screen)

    def process_render_debug(self):
        "Renders all values for debugging"
        if self.debug:
            if self.state in [THROWING_STATE, PLAYING_STATE]: self.space.debug_draw(self.options)
            debug_info = [f"{self.fps} ({FPS_LOCK}) fps", f"state: {STATES[self.state]} ({self.state})"]
            self.screen.blit(self.debug_font.render("\n".join(debug_info), True, "#FFFFFF", "#000000"), (0, 0))

    def run(self):
        "Runs main cycle"
        self.running = True
        self.state = MAIN_STATE
        pygame.mixer.music.play(-1)
        while self.running:
            self.time_delta = self.clock.tick(FPS_LOCK) / 1000.0
            self.fps = round(self.clock.get_fps())

            if self.state >= THROWING_STATE: pygame.mouse.set_visible(False)
            else: pygame.mouse.set_visible(True)

            "====---- Update ----===="
            self.process_events()
            self.process_player_events()
            self.process_controls()
            self.ui_manager.update(self.time_delta)
            if self.state == PLAYING_STATE: self.space.step(self.time_delta)

            "====----  Draw  ----===="
            self.screen.fill("#070707")
            self.process_render()
            # self.process_render_debug()

            #Displaying on window
            self.flip()
        pygame.quit()


#Launching the game
if __name__ == "__main__":
    PingPY().run()