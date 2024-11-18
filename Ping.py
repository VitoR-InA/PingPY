from _internal.classes.Bodies import Ball, Box, Player
from _internal.classes.Grid import Grid, draw_test_grid

from math import sin, cos, radians

from os.path import exists

import pickle as pkl

import pygame as pg
import pygame_gui as pggui
import pymunk as pm

from pygame_gui import UIManager
from pygame_gui.core import ObjectID
from pygame_gui.elements import UIButton, UIHorizontalSlider, UIAutoResizingContainer, UILabel, UIPanel
from pymunk import pygame_util as pgu

from random import randint

from typing import Tuple


def get_multiples(size, start, stop):
    "Returns multiples of a given size"
    result = []
    for i in range(start, stop + 1):
        if (size[0] * 10) % i == 0 and (size[1] // 2 * 10) % i == 0:
            result.append(i)
    return result


#Game states
MENU_STATE = 0
SHOP_STATE = 1
PREPARATION_STATE = 2
THROWING_STATE = 3
PLAYING_STATE = 4
DIED_STATE = 5
WINNED_STATE = 6

STATES = {val: var for var, val in globals().items() if var.endswith("_STATE")}


class PingPY:
    def __init__(self,
                 size: Tuple[int, int] = (0, 0),
                 flags: int = 0,
                 caption: str = "Window",
                 fps: int = 60,
                 theme_path: str = None):
        "====----       Init       ----===="
        #Pygame init
        pg.init()
        pg.mixer.init()
        
        #Defining user events
        self.TIMEREVENT = pg.USEREVENT + 3 #MIN 3, pggui using pygame.USEREVENT

        #Defining window vars
        self.size = size
        self.clock = pg.time.Clock()
        self.FPS = fps

        #Setting (0, 0) size to screen size for UIManager correct work
        if self.size == (0, 0):
            info = pg.display.Info()
            self.size = (info.current_w, info.current_h)
        
        self.size_factor = (1920 / self.size[0] / 2) + (1080 / self.size[1] / 2)
        
        divisors = get_multiples(self.size, 8, 20)

        self.sizes = (min(divisors), divisors[len(divisors) // 2], max(divisors))
            

        "====---- Pygame surfaces  ----===="
        #Window
        self.screen = pg.display.set_mode(self.size, flags)

        #UIManager surfaces
        self.manager = UIManager(self.size, theme_path)

        #Window title
        pg.display.set_caption(caption)


        "====----      Sounds      ----===="
        #Bodies sound channels
        self.master = pg.mixer.Channel(0)
        self.master.set_volume(1)
        pg.mixer.music.load("_internal\\sounds\\Music.wav")

        #Sounds var
        self.sounds = {}


        "====----   Pymunk init    ----===="
        #Pymunk space setup
        pgu.positive_y_is_up = False
        self.space = pm.Space()

        #Defining on collision handler
        collision_handler = self.space.add_collision_handler(1, 2)
        collision_handler.begin = self.on_collision

        #Defining debug draw options
        self.options = pgu.DrawOptions(self.screen)
        self.debug = False


        "====----  Pymunk bodies   ----===="
        #Defining ball vars
        self.angle = 90
        self.sounds["Jump1"] = pg.mixer.Sound("_internal\\sounds\\Jump.wav")
        self.sounds["Jump2"] = pg.mixer.Sound("_internal\\sounds\\Jump2.wav")

        #Defining player vars
        self.score = 0
        
        self.player_speed = 500
        self.player_health = 3
        
        self.autopilot = False
        self.sounds["PlayerWin"] = pg.mixer.Sound("_internal\\sounds\\playerWin.wav")
        self.sounds["PlayerDie"] = pg.mixer.Sound("_internal\\sounds\\PlayerDie.wav")
        self.sounds["GameStart"] = pg.mixer.Sound("_internal\\sounds\\GameStart.wav")
        self.sounds["GameExit"] = pg.mixer.Sound("_internal\\sounds\\GameExit.wav")

        #Defining walls
        Box(pg.Rect(-11, -11, self.size[0] + 21, self.size[1] + 50), 10, self.space)


        "====----       GUI        ----===="
        #Defining menu container
        self.menu_container = UIAutoResizingContainer(pg.Rect((0, 0), self.size), manager=self.manager)

        #Defining preparation container
        self.preparation_container = UIAutoResizingContainer(pg.Rect((0, 0), self.size), manager=self.manager)

        #Defining shop container
        self.shop_container = UIAutoResizingContainer(pg.Rect((0, 0), self.size), manager=self.manager)

        #Means default button size
        gui_size = (280 / self.size_factor, 80 / self.size_factor)
        spacing = 10 / self.size_factor

        "====----    Main menu     ----===="
        #Defining volume slider
        self.volume_sldr = UIHorizontalSlider(pg.Rect((10, self.size[1] - gui_size[1] - 10), gui_size),
                                              100, (0, 100), self.manager, self.menu_container)
        #Defining volume slider label
        UILabel(pg.Rect((10, self.size[1] - gui_size[1] - 10), gui_size),
                "Volume", self.manager, self.menu_container)

        #Defining play button
        self.play_btn = UIButton(pg.Rect((self.size[0] - gui_size[0] - spacing, self.size[1] - (gui_size[1] + spacing) * 3), gui_size),
                                 "Play", self.manager, self.menu_container)
        
        #Defining shop button
        self.shop_btn = UIButton(pg.Rect((self.size[0] - gui_size[0] - spacing, self.size[1] - (gui_size[1] + spacing) * 2), gui_size),
                                 "Shop", self.manager, self.menu_container)
        
        #Defining exit button
        self.exit_btn = UIButton(pg.Rect((self.size[0] - gui_size[0] - spacing, self.size[1] - (gui_size[1] + spacing)), gui_size),
                                 "Exit", self.manager, self.menu_container)

        "====---- Preparation menu ----===="
        #Defining preparation back button
        self.prep_back_btn = UIButton(pg.Rect((spacing, self.size[1] - gui_size[1] - spacing), (gui_size[1], ) * 2),
                                      "Back", self.manager, self.preparation_container)
        
        #Defining grid size slider
        self.size_sldr = UIHorizontalSlider(pg.Rect((gui_size[1] + spacing * 2, self.size[1] - gui_size[1] - spacing), gui_size),
                                            1, (0, 2), self.manager, self.preparation_container)
        self.grid_size = 1
        #Defining grid size slider label
        UILabel(pg.Rect((gui_size[1] + spacing * 2, self.size[1] - gui_size[1] - spacing), gui_size),
                "Size", self.manager, self.preparation_container)
        
        #Defining start button
        self.start_btn = UIButton(pg.Rect((self.size[0] - gui_size[0] - spacing, self.size[1] - (gui_size[1] + spacing)), gui_size),
                                  "Start", self.manager, self.preparation_container)

        "====----    Shop menu     ----===="
        #Defining shop back button
        self.shop_back_btn = UIButton(pg.Rect((spacing, self.size[1] - gui_size[1] - spacing), (gui_size[1], ) * 2),
                                      "Back", self.manager, self.shop_container)
        
        #Defining player speed upgrade
        self.player_speed_minus = UIButton(pg.Rect((self.size[0] / 2 - gui_size[1] / 2 - spacing - gui_size[0] / 2 - (gui_size[0] + spacing), self.size[1] - gui_size[1] - spacing), (gui_size[1] / 2, gui_size[1])),
                                           "-", self.manager, self.shop_container, "Speed -50\nScore +125\nMIN: 500")
        UIPanel(pg.Rect((self.size[0] / 2 - gui_size[0] / 2 - (gui_size[0] + spacing), self.size[1] - gui_size[1] - spacing), gui_size),
                manager=self.manager, container=self.shop_container)
        self.player_speed_lbl = UILabel(pg.Rect((self.size[0] / 2 - gui_size[0] / 2 - (gui_size[0] + spacing), self.size[1] - gui_size[1] - spacing), gui_size), "Speed",
                self.manager, self.shop_container)
        self.player_speed_plus = UIButton(pg.Rect((self.size[0] / 2 + gui_size[0] + spacing - gui_size[0] / 2 - (gui_size[0] + spacing), self.size[1] - gui_size[1] - spacing), (gui_size[1] / 2, gui_size[1])),
                                          "+", self.manager, self.shop_container, "Speed +50\nScore -250\nMAX: 1000")

        #Defining player health upgrade
        self.player_health_minus = UIButton(pg.Rect((self.size[0] / 2 - gui_size[1] / 2 - spacing - gui_size[0] / 2 + (gui_size[0] + spacing), self.size[1] - gui_size[1] - spacing), (gui_size[1] / 2, gui_size[1])),
                                           "-", self.manager, self.shop_container, "Health -1\nScore +250\nMIN: 3")
        UIPanel(pg.Rect((self.size[0] / 2 - gui_size[0] / 2 + (gui_size[0] + spacing), self.size[1] - gui_size[1] - spacing), gui_size),
                manager=self.manager, container=self.shop_container)
        self.player_health_lbl = UILabel(pg.Rect((self.size[0] / 2 - gui_size[0] / 2 + (gui_size[0] + spacing), self.size[1] - gui_size[1] - spacing), gui_size), "Health",
                self.manager, self.shop_container)
        self.player_health_plus = UIButton(pg.Rect((self.size[0] / 2 + gui_size[0] + spacing - gui_size[0] / 2 + (gui_size[0] + spacing), self.size[1] - gui_size[1] - spacing), (gui_size[1] / 2, gui_size[1])),
                                          "+", self.manager, self.shop_container, "Health +1\nScore -500\nMAX: 5")

        UIButton(pg.Rect((self.size[0] - gui_size[0] - gui_size[1] - spacing * 2, spacing), (gui_size[1], ) * 2),
                         "?", self.manager, self.shop_container,
                         "You can see all the information about the upgrades when you hover over them.",
                         object_id=ObjectID(object_id="#question_button"))
        self.player_score_pnl = UIPanel(pg.Rect((self.size[0] - gui_size[0] - spacing, spacing), gui_size),
                                        manager=self.manager)
        self.player_score_lbl = UILabel(pg.Rect((self.size[0] - gui_size[0] - spacing, spacing), gui_size), "Score", self.manager)


        "====----      Fonts       ----===="
        #Defining debug font
        self.debug_font = pg.Font("_internal\\fonts\\Default.otf", 20 // int(self.size_factor))

        #Defining header font
        self.header_font = pg.Font("_internal\\fonts\\Default.otf", 170 // int(self.size_factor))
        
        
        "====----    Data load     ----===="
        if exists("_internal\\Ping.data"):
            self.load_data()


    def draw_arrow(self, center: Tuple[float, float], angle: int):
        "Draws arrow at given coordinates, defines ball direction"
        self.end_x = center[0] + 50 * cos(radians(angle))
        self.end_y = center[1] - 50 * sin(radians(angle))

        left_end_x = self.end_x + 25 * cos(radians(angle + 140))
        left_end_y = self.end_y - 25 * sin(radians(angle + 140))
        right_end_x = self.end_x + 25 * cos(radians(angle - 140))
        right_end_y = self.end_y - 25 * sin(radians(angle - 140))

        pg.draw.line(self.screen, "#FFFFFF", (self.end_x, self.end_y), (left_end_x, left_end_y), 3)
        pg.draw.line(self.screen, "#FFFFFF", (self.end_x, self.end_y), (right_end_x, right_end_y), 3)


    def player_take_damage(self, damage: int = 1):
        """
        Deals damage to player

        Args:
            damage (int): Defines how much damage the player takes
        """
        self.master.play(self.sounds["GameExit"])
        self.player.reset_position()
        self.ball.reset_position()
        self.player.health -= damage
        self.angle = 90
        self.state = THROWING_STATE
        
        
    def end_level(self):
        "Stops current level"
        # Удаляем все формы и тела, связанные с сеткой
        for body in self.grid.get_bodies():
            for shape in body.shapes:
                if shape in self.space.shapes:
                    self.space.remove(shape)
            if body in self.space.bodies:
                self.space.remove(body)
        
        # Удаляем формы и тела игрока и мяча
        if self.player.shape in self.space.shapes:
            self.space.remove(self.player.shape)
        if self.player.body in self.space.bodies:
            self.space.remove(self.player.body)
        if self.ball.shape in self.space.shapes:
            self.space.remove(self.ball.shape)
        if self.ball.body in self.space.bodies:
            self.space.remove(self.ball.body)
        
        self.state = MENU_STATE
        self.save_data()
        
        pg.mixer.music.unpause()


    def on_collision(self, arbiter: pm.arbiter.Arbiter, space: pm.Space, data):
        "Removes grid body on collision"
        space.remove(arbiter.shapes[1].body, arbiter.shapes[1])
        for shape in self.grid.get_shapes():
            if shape == arbiter.shapes[1]:
                self.grid.remove(arbiter.shapes[1].body, arbiter.shapes[1])
        self.master.play(self.sounds[f"Jump{randint(1, 2)}"])
        self.score += 5
        return True
    
    
    def save_data(self):
        with open("_internal\\Ping.data", "wb") as file:
            data = {"game":{"volume":pg.mixer.music.get_volume(), "size":self.grid_size},
                    "player":{"speed":self.player_speed, "health":self.player_health, "score":self.score}}
            pkl.dump(data, file)
            
    def load_data(self):
        with open("_internal\\Ping.data", "rb") as file:
            data = pkl.load(file)
            
            volume = data["game"]["volume"]
            self.volume_sldr.set_current_value(volume * 100)
            pg.mixer.music.set_volume(volume)
            self.master.set_volume(volume)
            
            size = data["game"]["size"]
            self.size_sldr.set_current_value(size)
            self.grid_size = size
            
            player = data["player"]
            self.player_speed = player["speed"]
            self.player_health = player["health"]
            self.score = player["score"]


    def run(self):
        "Runs main cycle"
        running = True

        self.state = MENU_STATE

        pg.mixer.music.play(-1)
        while running:
            delta = self.clock.tick(self.FPS) / 1000.0
            fps = round(self.clock.get_fps())


            if self.state >= THROWING_STATE:
                pg.mouse.set_visible(False)
            else:
                pg.mouse.set_visible(True)

            keys = pg.key.get_pressed()


            "====---- Pygame events ----===="
            #Getting all pygame events
            for event in pg.event.get():


                #Adding pygame GUI events to other
                self.manager.process_events(event)


                "====---- Quit event ----===="
                if event.type == pg.QUIT:
                    self.save_data()
                    running = False


                "====---- Keydown event ----===="
                if event.type == pg.KEYDOWN:

                    #Toggle debug
                    if event.key == pg.K_F3:
                        self.debug = not self.debug

                    #Throw ball
                    if self.state == THROWING_STATE and event.key == pg.K_SPACE:
                        self.ball_speed = [vel * 20 for vel in self.ball_start_velocity]
                        self.ball.body.velocity = self.ball_speed
                        self.state = PLAYING_STATE

                    if self.state == PLAYING_STATE and self.player.health > 1 and event.key == pg.K_q:
                        self.player_take_damage()

                    #End current level
                    if event.key == pg.K_ESCAPE:
                        if THROWING_STATE <= self.state <= PLAYING_STATE:
                            self.end_level()
                        elif self.state == SHOP_STATE:
                            self.state = MENU_STATE


                "====---- Timer event ----===="
                if event.type == self.TIMEREVENT:
                    if self.state == WINNED_STATE:
                        self.score += (500 * (self.grid_size + 1) + self.player.health * 25)
                    self.end_level()


                "====---- Button event ----===="
                if event.type == pggui.UI_BUTTON_PRESSED:

                    #Play button
                    if event.ui_element == self.play_btn:
                        self.state = PREPARATION_STATE

                    #Start button
                    if event.ui_element == self.start_btn:
                        self.state = THROWING_STATE
                        self.player = Player((250, 20), self.player_health, self.space)
                        self.ball = Ball(10, (255, 0, 0, 255), self.space)
                        self.angle = 90
                        self.grid = Grid((self.sizes[self.grid_size], self.sizes[self.grid_size]), self.space)
                        pg.mixer.music.pause()
                        self.master.play(self.sounds["GameStart"])

                    #Shop button
                    if event.ui_element == self.shop_btn:
                        self.state = SHOP_STATE

                    #Shop back button
                    if event.ui_element == self.shop_back_btn or event.ui_element == self.prep_back_btn:
                        self.state = MENU_STATE
                        
                    "====---- Upgrades ----===="
                    #Speed upgrade
                    if event.ui_element == self.player_speed_minus and self.player_speed > 500:
                        self.score += 125
                        self.player_speed -= 50
                    
                    if event.ui_element == self.player_speed_plus and self.score >= 250 and self.player_speed < 1000:
                        self.score -= 250
                        self.player_speed += 50
                        
                    #Health upgrade
                    if event.ui_element == self.player_health_minus and self.player_health > 3:
                        self.score += 250
                        self.player_health -= 1
                    
                    if event.ui_element == self.player_health_plus and self.score >= 500 and self.player_health < 10:
                        self.score -= 500
                        self.player_health += 1

                    #Exit button
                    if event.ui_element == self.exit_btn:
                        self.master.play(self.sounds["GameExit"])
                        pg.time.delay(220)
                        running = False
                
                "====---- Slider event ----===="
                if event.type == pggui.UI_HORIZONTAL_SLIDER_MOVED:
                    if event.ui_element == self.volume_sldr:
                        pg.mixer.music.set_volume(event.value / 100)
                        self.master.set_volume(event.value / 100)
                    
                    if event.ui_element == self.size_sldr:
                        self.grid_size = event.value


            "====---- Player control ----===="
            if self.state >= THROWING_STATE:

                #Left
                if keys[pg.K_a] or keys[pg.K_LEFT]:
                    if self.state == THROWING_STATE and self.angle < 135:
                        self.angle += 100 * delta
                        
                    if self.state == PLAYING_STATE and self.player.body.position[0] - self.player.rect.size[0] / 2 > 0:
                        self.player.body.velocity = (-self.player_speed, 0)
                        
                    else: self.player.body.velocity = (0, 0)

                #Right
                elif keys[pg.K_d] or keys[pg.K_RIGHT]:
                    if self.state == THROWING_STATE and self.angle > 45:
                        self.angle -= 100 * delta
                        
                    if self.state == PLAYING_STATE and self.player.body.position[0] + self.player.rect.size[0] / 2 < self.size[0]:
                        self.player.body.velocity = (self.player_speed, 0)
                        
                    else:
                        self.player.body.velocity = (0, 0)

                #No pressed keys
                else:
                    self.player.body.velocity = (0, 0)
                    
                    
            "====---- Score show ----===="
            if self.state == SHOP_STATE or THROWING_STATE <= self.state <= PLAYING_STATE and keys[pg.K_TAB]:
                self.player_score_lbl.set_text(f"Score: {self.score}")
                self.player_score_pnl.show()
                self.player_score_lbl.show()
            else:
                self.player_score_pnl.hide()
                self.player_score_lbl.hide()


            "====---- Autopilot ----===="
            if self.autopilot:
                self.player.body.position = (self.ball.body.position[0], self.player.body.position[1])


            "====---- Player events ----===="
            "     WIN / DIE / TAKE DMG     "
            if THROWING_STATE <= self.state <= PLAYING_STATE:
                #Decrease player's health by 1
                if self.ball.body.position[1] > self.size[1]:
                    self.player_take_damage()

                #Game over when the player's health == 0
                if not self.player.health:
                    pg.time.set_timer(self.TIMEREVENT, 2500, 1)
                    self.master.play(self.sounds["PlayerDie"])
                    self.state = DIED_STATE

                #Game win when ball breaks all grid bodies
                if not len(self.grid.get_shapes()):
                    pg.time.set_timer(self.TIMEREVENT, 2500, 1)
                    self.master.play(self.sounds["PlayerWin"])
                    self.state = WINNED_STATE


            "====---- Update ----===="
            #UIManager update
            self.manager.update(delta)

            if self.state == PLAYING_STATE:
                #Pymunk space update
                self.space.step(delta)

            #Pygame screen update
            self.screen.fill("#070707")


            "====---- Draw arrow ----===="
            if self.state == THROWING_STATE:
                #Drawing arrow
                self.draw_arrow(self.ball.body.position, self.angle)

                #Setting start ball velocity | direction
                self.ball_start_velocity = (self.end_x - self.ball.body.position[0],
                                            self.end_y - self.ball.body.position[1])


            "====---- Other GUI draw ----===="
            if self.state == MENU_STATE:
                #Drawing game title
                self.screen.blit(self.header_font.render("PingPY", True, "#FFFFFF"), (10, 10))
                self.menu_container.show()
                self.preparation_container.hide()
                self.shop_container.hide()

            elif self.state == SHOP_STATE:
                #Drawing game title
                self.screen.blit(self.header_font.render("Shop", True, "#FFFFFF"), (10, 10))
                self.menu_container.hide()
                self.preparation_container.hide()
                self.shop_container.show()
                
                self.player_speed_lbl.set_text(f"Speed: {self.player_speed}")
                
                self.player_health_lbl.set_text(f"Health: {self.player_health}")
                
                
            elif self.state == PREPARATION_STATE:
                self.menu_container.hide()
                self.preparation_container.show()
                self.shop_container.hide()

                draw_test_grid((self.sizes[self.grid_size], self.sizes[self.grid_size]), self.screen)
            
            elif THROWING_STATE <= self.state <= PLAYING_STATE:
                self.menu_container.hide()
                self.preparation_container.hide()
                self.shop_container.hide()

                #Drawing player
                self.player.draw(self.screen)

                #Drawing ball
                self.ball.draw(self.screen)

                #Drawing grid
                self.grid.draw(self.screen)

            elif self.state == DIED_STATE:
                #Drawing game over text
                text = self.header_font.render("Game over!", True, "#FFFFFF")
                self.screen.blit(text, (self.size[0] / 2 - text.width / 2, self.size[1] / 2 - text.height / 2))

            elif self.state == WINNED_STATE:
                #Drawing game win text
                text = self.header_font.render("Game win!", True, "#FFFFFF")
                self.screen.blit(text, (self.size[0] / 2 - text.width / 2, self.size[1] / 2 - text.height / 2))


            #Drawing manager GUI
            self.manager.draw_ui(self.screen)


            "====---- Debug ----===="
            if self.debug:
                if self.state >= THROWING_STATE:
                    #Drawing pymunk debug draw
                    self.space.debug_draw(self.options)

                #Drawing current fps
                self.screen.blit(self.debug_font.render(f"{fps} fps", True, "#FFFFFF", "#000000"), (0, 0))

                #Drawing the value of the state var
                self.screen.blit(self.debug_font.render(f"state: {STATES[self.state]} ({self.state})", True, "#FFFFFF", "#000000"), (0, 24))
                
                #Drawing the value of the grid size var
                self.screen.blit(self.debug_font.render(f"grid size: {(self.sizes[self.grid_size], self.sizes[self.grid_size])})", True, "#FFFFFF", "#000000"), (0, 48))


            #Displaying on window
            pg.display.update()
        pg.quit()


#Launching the game
if __name__ == "__main__":
    ping = PingPY(flags=pg.NOFRAME, caption="PingPY", theme_path="_internal\\theme.json")
    ping.run()