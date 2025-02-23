from _internal.game_modules.bodies import Ball
from _internal.game_modules.bodies import HollowBox
from _internal.game_modules.bodies import Player

from _internal.game_modules.constants import *

from _internal.game_modules.grid import Grid

import os
import sys

import pygame
from pygame import Rect
from pygame import Window

import pygame_gui
from pygame_gui import UIManager
from pygame_gui.core import UIContainer
from pygame_gui.elements import UIButton, UILabel, UIHorizontalSlider, UIPanel

import pymunk
from pymunk import pygame_util

from random import randint

import timer


class PingPY(Window):
    def __init__(self):
        "====----       Init       ----===="
        #Pygame init
        pygame.init()
        pygame.mixer.init()

        super().__init__("PingPY", fullscreen_desktop = True)

        #Defining window vars
        self.clock = pygame.time.Clock()

        size_factor = (1920 / self.size[0] / 2) + (1080 / self.size[1] / 2)

        multiples = self.get_multiples(self.size, 8, 20)
        self.sizes = (min(multiples), multiples[len(multiples) // 2], max(multiples))


        "====---- Pygame surfaces  ----===="
        #Main window surface
        self.screen = self.get_surface()

        #UIManager surface
        self.ui_manager = UIManager(self.size, "_internal\\theme.json")


        "====----      Sounds      ----===="
        #Master pygame channel
        self.master = pygame.mixer.Channel(0)

        #Sounds var
        self.sounds = {}

        #Ball sounds
        self.sounds["jump1"] = pygame.mixer.Sound("_internal\\sounds\\ball\\jump.wav")
        self.sounds["jump2"] = pygame.mixer.Sound("_internal\\sounds\\ball\\jump2.wav")

        #Player sounds
        self.sounds["player_damage"] = pygame.mixer.Sound("_internal\\sounds\\player\\damage.wav")
        self.sounds["player_die"] = pygame.mixer.Sound("_internal\\sounds\\player\\die.wav")
        self.sounds["player_win"] = pygame.mixer.Sound("_internal\\sounds\\player\\win.wav")

        #Game sounds
        self.sounds["game_start"] = pygame.mixer.Sound("_internal\\sounds\\game\\start.wav")

        #Game music
        pygame.mixer.music.load("_internal\\Sounds\\music.wav")


        "====----   Pymunk init    ----===="
        #Pymunk space setup
        pygame_util.positive_y_is_up = False
        self.space = pymunk.Space()

        #Defining on collision handler
        collision_handler = self.space.add_collision_handler(1, 2)
        collision_handler.begin = self.process_collision

        #Defining debug draw options
        self.options = pygame_util.DrawOptions(self.screen)
        self.debug = False


        "====----    Game vars     ----===="
        #Defining ball vars
        self.ball_color = BALL_DEFAULT_COLOR
        self.ball_pos = (self.size[0] / 2, self.size[1] - 100)
        self.ball_radius = BALL_DEFAULT_RADIUS

        #Defining player vars
        self.player_health = PLAYER_DEFAULT_HEALTH
        self.player_score = PLAYER_DEFAULT_SCORE
        self.player_size = PLAYER_DEFAULT_SIZE
        self.player_speed = PLAYER_DEFAULT_SPEED
        self.player_pos = (self.size[0] / 2, self.size[1] - 50)

        #Defining walls
        HollowBox(Rect(-11, -11, self.size[0] + 21, self.size[1] + 50), 10, self.space)


        "====----       GUI        ----===="
        #Means default gui element size
        gui_size = (280 / size_factor, 80 / size_factor)
        spacing = 5 / size_factor
        temp_rect = Rect()

        "====----    Main menu     ----===="
        #Defining menu container
        self.menu_container = UIContainer(self.screen.get_rect(), manager = self.ui_manager)

        #Defining volume slider
        temp_rect.size = gui_size
        temp_rect.bottomleft = (spacing, - spacing)
        self.volume_sldr = UIHorizontalSlider(temp_rect, 100, (0, 100), self.ui_manager, self.menu_container,
                                              anchors = {"bottom":"bottom"})
        #Defining volume slider label
        UILabel(temp_rect, "Volume", self.ui_manager, self.menu_container,
                anchors = {"bottom":"bottom"})

        #Defining play button
        temp_rect.bottomright = (-spacing, -(spacing * 3 + gui_size[1] * 2))
        UIButton(temp_rect, "Play", self.ui_manager, self.menu_container, command = lambda: self.goto("PREPARATION"),
                 anchors = {"right":"right", "bottom":"bottom"})

        #Defining shop button
        temp_rect.bottomright = (-spacing, -(spacing * 2 + gui_size[1]))
        UIButton(temp_rect, "Shop", self.ui_manager, self.menu_container, command = lambda: self.goto("SHOP"),
                 anchors = {"right":"right", "bottom":"bottom"})

        #Defining exit button
        temp_rect.bottomright = (-spacing, -spacing)
        UIButton(temp_rect, "Exit", self.ui_manager, self.menu_container, command = lambda: setattr(self, "running", False),
                 anchors = {"right":"right", "bottom":"bottom"})

        "====---- Preparation menu ----===="
        #Defining preparation container
        self.preparation_container = UIContainer(self.screen.get_rect(), manager = self.ui_manager, visible = False)

        #Defining preparation back button
        temp_rect.size = (gui_size[1], ) * 2
        temp_rect.bottomleft = (spacing, -spacing)
        UIButton(temp_rect, "Back", self.ui_manager, self.preparation_container, command = lambda: self.goto("MENU"),
                 anchors = {"bottom":"bottom"})

        #Defining grid size slider
        temp_rect.size = gui_size
        temp_rect.bottomleft = (spacing * 2 + gui_size[1], -spacing)
        self.size_sldr = UIHorizontalSlider(temp_rect, 1, (0, 2), self.ui_manager, self.preparation_container,
                                            anchors = {"bottom":"bottom"})
        #Defining grid size slider label
        UILabel(temp_rect, "Size", self.ui_manager, self.preparation_container,
                anchors = {"bottom":"bottom"})
        self.grid_size = 1

        #Defining start button
        temp_rect.bottomright = (-spacing, - spacing)
        UIButton(temp_rect, "Start", self.ui_manager, self.preparation_container, command = self.new_level,
                 anchors = {"right":"right", "bottom":"bottom"})

        "====----    Shop menu     ----===="
        #Defining shop container
        self.shop_container = UIContainer(self.screen.get_rect(), manager = self.ui_manager, visible = False)

        #Defining shop back button
        temp_rect.size = (gui_size[1], ) * 2
        temp_rect.bottomleft = (spacing, -spacing)
        UIButton(temp_rect, "Back", self.ui_manager, self.shop_container, command = lambda: self.goto("MENU"),
                 anchors = {"bottom":"bottom"})

        #Defining player speed upgrade
        temp_rect.size = gui_size
        temp_rect.bottomright = (-spacing, -spacing)
        UIPanel(temp_rect, manager = self.ui_manager, container = self.shop_container,
                anchors = {"centerx":"centerx", "bottom":"bottom"})
        self.player_speed_lbl = UILabel(temp_rect, "Speed", self.ui_manager, self.shop_container,
                                        anchors = {"centerx":"centerx", "bottom":"bottom"})

        #Defining player health upgrade
        temp_rect.size = gui_size
        temp_rect.bottomleft = (gui_size[0] + spacing, -spacing)
        UIPanel(temp_rect, manager = self.ui_manager, container = self.shop_container,
                anchors = {"centerx":"centerx", "bottom":"bottom"})
        self.player_health_lbl = UILabel(temp_rect, "Health", self.ui_manager, self.shop_container,
                                         anchors = {"centerx":"centerx", "bottom":"bottom"})


        #LEFT TARGET ISSUE: https://github.com/MyreMylar/pygame_gui/issues/671
        self.player_speed_minus = UIButton(Rect((-(gui_size[0] + gui_size[1] + spacing), -(gui_size[1] + spacing)), (gui_size[1], ) * 2),
                                           "-", self.ui_manager, self.shop_container, "Speed -50\nScore +125\nMIN: 500",
                                           anchors = {"left_target":self.player_speed_lbl, "bottom":"bottom"})
        self.player_speed_plus = UIButton(Rect((spacing, -(gui_size[1] + spacing)), (gui_size[1], ) * 2),
                                          "+", self.ui_manager, self.shop_container, "Speed +50\nScore -250\nMAX: 1000",
                                          anchors = {"left_target":self.player_speed_lbl, "bottom":"bottom"})

        self.player_health_minus = UIButton(Rect((-(gui_size[0] + gui_size[1] + spacing), -(gui_size[1] + spacing)), (gui_size[1], ) * 2),
                                            "-", self.ui_manager, self.shop_container, "Health -1\nScore +250\nMIN: 3",
                                            anchors = {"left_target":self.player_health_lbl, "bottom":"bottom"})
        self.player_health_plus = UIButton(Rect((spacing, -(gui_size[1] + spacing)), (gui_size[1], ) * 2),
                                           "+", self.ui_manager, self.shop_container, "Health +1\nScore -500\nMAX: 5",
                                           anchors = {"left_target":self.player_health_lbl, "bottom":"bottom"})

        "====----   Score label    ----===="
        #Defining score container
        self.player_score_container = UIContainer(self.screen.get_rect(), manager = self.ui_manager, visible = False)

        temp_rect.size = gui_size
        temp_rect.topright = (-spacing, spacing)
        UIPanel(temp_rect, manager = self.ui_manager, container = self.player_score_container, anchors = {"right":"right", "top":"top"})
        self.player_score_lbl = UILabel(temp_rect, "Score", self.ui_manager, self.player_score_container, anchors = {"right":"right", "top":"top"})


        "====----      Fonts       ----===="
        #Defining debug font
        self.debug_font = pygame.sysfont.SysFont("NotoSans", 20 // int(size_factor))

        #Defining header font
        self.header_font = pygame.sysfont.SysFont("NotoSans", 170 // int(size_factor))


    @classmethod
    def get_multiples(self, size, start, stop):
        "Returns multiples of a given size"
        result = []
        for i in range(start, stop + 1):
            if (size[0] * 10) % i == 0 and (size[1] // 2 * 10) % i == 0:
                result.append(i)
        return result


    @classmethod
    def get_workpath(self):
        if hasattr(sys, "frozen"): return sys._MEIPASS
        else: return os.path.join(os.path.abspath(__file__), "_internal")


    def goto(self, state: str):
        self.state = list(STATES.values()).index(f"{state.upper()}_STATE")
        for container in [attr for attr in dir(self) if attr.endswith("_container")]:
            if container.startswith(state.lower()):
                getattr(self, container).show()
            else: getattr(self, container).hide()


    def reset_player(self, damage: int):
        self.master.play(self.sounds["player_damage"])
        self.player.take_damage(damage)
        self.player.set_position(self.player_pos)
        self.ball.set_position(self.ball_pos)
        self.ball.set_angle(90)
        self.goto("THROWING")


    def new_level(self):
        "Starts new level"
        self.player = Player(Rect(self.player_pos, self.player_size), self.player_health, self.player_speed, self.space)
        self.ball = Ball(self.ball_color, self.ball_pos, self.ball_radius, self.space)
        self.grid = Grid(Rect((0, 0), (self.size[0], self.size[1] / 2)), (self.sizes[self.grid_size], self.sizes[self.grid_size]), self.space)
        pygame.mixer.music.pause()
        self.master.play(self.sounds["game_start"])
        self.goto("THROWING")


    def end_level(self, timer_id = None, time = None):
        "Stops current level"
        if timer_id: timer.kill_timer(timer_id)
        self.grid.clear()
        self.space.remove(self.player.body, self.player.shape)
        self.space.remove(self.ball.body, self.ball.shape)
        pygame.mixer.music.unpause()
        self.goto("MENU")


    def process_collision(self, arbiter: pymunk.arbiter.Arbiter, space: pymunk.Space, data):
        "Processes collisions between the ball and the grid body"
        collided_shape = arbiter.shapes[1]
        space.remove(collided_shape.body, collided_shape)
        self.grid.remove(collided_shape.body, collided_shape)
        self.master.play(self.sounds[f"jump{randint(1, 2)}"])
        self.player_score += 5
        return True


    def process_events(self):
        "Processes all pygame and pygame_gui events"
        "====---- Pygame events ----===="
        #Getting all pygame events
        for event in pygame.event.get():

            #Adding pygame GUI events to other
            self.ui_manager.process_events(event)


            "====---- Quit event ----===="
            if event.type == pygame.QUIT: self.running = False

            "====---- Button event ----===="
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                "====---- Upgrades ----===="
                #Speed upgrade
                if event.ui_element == self.player_speed_minus and self.player_speed > 500:
                    self.player_score += 125
                    self.player_speed -= 50

                if event.ui_element == self.player_speed_plus and self.player_score >= 250 and self.player_speed < 1000:
                    self.player_score -= 250
                    self.player_speed += 50

                #Health upgrade
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
                    self.grid_size = event.value


    def process_controls(self):
        "Processes all keystrokes"
        "====---- Player control ----===="
        holded_keys = pygame.key.get_pressed()
        pressed_keys = pygame.key.get_just_pressed()

        "====----  Holded keys   ----===="
        if self.state == SHOP_STATE or (holded_keys[pygame.K_TAB] and self.state != SHOP_STATE):
            self.player_score_lbl.set_text(f"Score: {self.player_score}")
            self.player_score_container.show()
        else: self.player_score_container.hide()

        if hasattr(self, "player") and hasattr(self, "ball"):
            if holded_keys[pygame.K_a] or holded_keys[pygame.K_LEFT]:
                if self.state == THROWING_STATE and self.ball.angle < 135:
                    self.ball.angle += 100 * self.time_delta

                if self.state == PLAYING_STATE and self.player.body.position[0] - self.player.rect.size[0] / 2 > 0:
                    self.player.body.velocity = (-self.player.speed, 0)

                else: self.player.body.velocity = (0, 0)

            elif holded_keys[pygame.K_d] or holded_keys[pygame.K_RIGHT]:
                if self.state == THROWING_STATE and self.ball.angle > 45:
                    self.ball.angle -= 100 * self.time_delta

                if self.state == PLAYING_STATE and self.player.body.position[0] + self.player.rect.size[0] / 2 < self.size[0]:
                    self.player.body.velocity = (self.player.speed, 0)

                else: self.player.body.velocity = (0, 0)

            else: self.player.body.velocity = (0, 0)

        "====----  Pressed keys  ----===="
        if pressed_keys[pygame.K_F3]: self.debug = not self.debug # Toggle debug

        if self.state == THROWING_STATE and pressed_keys[pygame.K_SPACE]:
            self.ball_speed = [vel * 20 for vel in self.ball_start_velocity]
            self.ball.body.velocity = self.ball_speed
            self.state = PLAYING_STATE

        if self.state == PLAYING_STATE and pressed_keys[pygame.K_q]:
             self.reset_player(PLAYER_DEFAULT_DAMAGE)

        if pressed_keys[pygame.K_ESCAPE]:
            if self.state in [THROWING_STATE, PLAYING_STATE]: self.end_level()
            elif self.state in [SHOP_STATE, PREPARATION_STATE]: self.goto("MENU")


    def process_player_events(self):
        "Processes player events. Such as winning, losing, and taking damage."
        if self.state == PLAYING_STATE:
            #Decrease player's health by 1
            if self.ball.body.position[1] > self.size[1]:
                self.reset_player(PLAYER_DEFAULT_DAMAGE)

            #Game over when the player's health == 0
            if not self.player.health:
                self.player_score += (500 * (self.grid_size + 1) + self.player.health * 25)
                timer.set_timer(2000, self.end_level)
                self.master.play(self.sounds["player_die"])
                self.goto("DIED")

            #Game win when ball breaks all grid bodies
            if not len(self.grid.shapes):
                timer.set_timer(2000, self.end_level)
                self.master.play(self.sounds["player_win"])
                self.goto("WINNED")


    def process_render(self):
        if self.state == THROWING_STATE: self.ball_start_velocity = self.ball.draw_arrow(self.screen)

        if self.state == MENU_STATE: self.screen.blit(self.header_font.render("PingPY", True, "#FFFFFF"), (10, 0))

        elif self.state == SHOP_STATE:
            self.screen.blit(self.header_font.render("Shop", True, "#FFFFFF"), (10, 0))
            self.player_speed_lbl.set_text(f"Speed: {self.player_speed}")
            self.player_health_lbl.set_text(f"Health: {self.player_health}")

        elif self.state == PREPARATION_STATE: Grid.draw_preview(Rect((0, 0), (self.size[0], self.size[1] / 2)),
                                                                (self.sizes[self.grid_size], self.sizes[self.grid_size]), self.screen)
            
        elif self.state in [THROWING_STATE, PLAYING_STATE]:
            self.player.draw(self.screen)
            self.ball.draw(self.screen)
            self.grid.draw(self.screen)

        elif self.state == DIED_STATE:
            #Drawing game over text
            text = self.header_font.render("Game over!", True, "#FFFFFF")
            self.screen.blit(text, (self.size[0] / 2 - text.width / 2, self.size[1] / 2 - text.height / 2))

        elif self.state == WINNED_STATE:
            #Drawing game win text
            text = self.header_font.render("Game win!", True, "#FFFFFF")
            self.screen.blit(text, (self.size[0] / 2 - text.width / 2, self.size[1] / 2 - text.height / 2))


    def process_render_debug(self):
        "Renders all values for debugging"
        if self.debug:
            if self.state in [THROWING_STATE, PLAYING_STATE]: self.space.debug_draw(self.options)
            debug_info = [f"{self.fps} ({FPS_LOCK}) fps", f"state: {STATES[self.state]} ({self.state})"]
            self.screen.blit(self.debug_font.render("\n".join(debug_info), True, "#FFFFFF", "#000000"), (0, 0))


    def run(self):
        "Runs main cycle"
        self.running = True
        self.state = MENU_STATE
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
            self.ui_manager.draw_ui(self.screen)
            self.process_render()
            self.process_render_debug()

            #Displaying on window
            self.flip()
        pygame.quit()


#Launching the game
if __name__ == "__main__":
    PingPY().run()