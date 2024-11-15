from _internal.classes.Bodies import Ball, Box, Player
from _internal.classes.Grid import Grid

from math import sin, cos, radians

import pygame as pg
import pygame_gui as pggui
import pymunk as pm

from pygame_gui import UIManager
from pygame_gui.elements import UIButton, UIHorizontalSlider, UILabel
from pymunk import pygame_util as pgu

from random import randint

from typing import Tuple


def get_divisors(num, start, stop):
    result = []
    for i in range(start, stop):
        if (num * 10) % i == 0:
            result.append(i)
    return result


class Game:
    def __init__(self,
                 size: Tuple[int, int],
                 flags: int = 0,
                 caption: str = "Window",
                 fps: int = 60,
                 theme_path: str = None):
        "Init"
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


        "Pygame surfaces"
        #Window
        self.screen = pg.display.set_mode(self.size, flags)

        #UIManager surface
        self.manager = UIManager(self.size, theme_path)

        #Window title
        pg.display.set_caption(caption)
        
        
        "Sounds"
        #Bodies sound channels
        self.master = pg.mixer.Channel(0)
        self.master.set_volume(1)
        pg.mixer.music.load("_internal\\sounds\\Music.wav")
        
        #Sounds var
        self.sounds = {}


        "Pymunk init"
        #Pymunk space setup
        pgu.positive_y_is_up = False
        self.space = pm.Space(True)
        self.space.threads = 4

        #Defining on collision handler
        collision_handler = self.space.add_collision_handler(1, 2)
        collision_handler.begin = self.on_collision

        #Defining debug draw options
        self.options = pgu.DrawOptions(self.screen)
        self.debug = False


        "Pymunk bodies"
        #Defining ball vars
        self.sounds["Jump1"] = pg.mixer.Sound("_internal\\sounds\\Jump.wav")
        self.sounds["Jump2"] = pg.mixer.Sound("_internal\\sounds\\Jump2.wav")

        #Defining player vars
        self.autopilot = False
        self.sounds["PlayerWin"] = pg.mixer.Sound("_internal\\sounds\\playerWin.wav")
        self.sounds["PlayerDie"] = pg.mixer.Sound("_internal\\sounds\\PlayerDie.wav")
        self.sounds["GameStart"] = pg.mixer.Sound("_internal\\sounds\\GameStart.wav")
        self.sounds["GameExit"] = pg.mixer.Sound("_internal\\sounds\\GameExit.wav")

        #Defining walls
        Box(pg.Rect(-11, -11, self.size[0] + 21, self.size[1] + 50), 10, self.space)


        "GUI"
        self.elements = []
        
        #Defining volume slider
        self.volume_sldr = UIHorizontalSlider(pg.Rect(10, self.size[1] - 90, 280, 80), 100, (0, 100), self.manager)
        self.elements.append(self.volume_sldr)
        
        #Defining slider label
        self.volume_lbl = UILabel(pg.Rect(10, self.size[1] - 90, 280, 80), "Volume", self.manager)
        self.elements.append(self.volume_lbl)

        #Defining start button
        self.start_btn = UIButton(pg.Rect((self.size[0] - 290, self.size[1] - 180), (280, 80)), "Start", self.manager)
        self.elements.append(self.start_btn)
        
        #Defining exit button
        self.exit_btn = UIButton(pg.Rect((self.size[0] - 290, self.size[1] - 90), (280, 80)), "Exit", self.manager)
        self.elements.append(self.exit_btn)


        "Fonts"
        #Defining debug font
        self.debug_font = pg.Font("_internal\\fonts\\Default.otf", 20)

        #Defining header font
        self.header_font = pg.Font("_internal\\fonts\\Default.otf", 170)


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


    def new_ball(self,
                 radius: int,
                 position: Tuple[float, float],
                 color: Tuple[int, int, int, int],
                 space: pm.Space):
        """
        Creates Ball class copy

        Args:
            radius (int): ball radius
            position (Tuple[float, float]): ball center position
            color (Tuple[int, int, int, int]): ball shape color
            space (pm.Space): pymunk space
        """
        self.ball = Ball(1, position, radius, color, space)
        self.ball_start_velocity = (0, 0)
        self.angle = 90
        
        
    def new_grid(self,
                 size: Tuple[int, int],
                 count: Tuple[int, int],
                 space: pm.Space):
        """
        Creates Grid class copy

        Args:
            size (Tuple[int, int]): grid size
            count (Tuple[int, int]): bodies count in grid
            space (pm.Space): pymunk space
        """
        self.grid = Grid(pg.Rect((0, 0), size), count, space)


    def new_player(self,
                   size: Tuple[int, int],
                   speed: int,
                   color: Tuple[int, int, int, int],
                   space: pm.Space):
        """
        Creates Player class copy

        Args:
            size (Tuple[int, int]): player size
            speed (int): player speed
            color (Tuple[int, int, int, int]): player shape color
            space (pm.Space): pymunk space
        """
        self.player = Player(pg.Rect((self.size[0] / 2, self.size[1] - 50), size), color, space)
        self.player_speed = speed


    def end_level(self):
        "Stops current level"
        for shape in self.grid.get_shapes():
            self.space.remove(shape)
            self.grid.remove_shape(shape)
        self.space.remove(self.player.shape, self.ball.shape)
        self.set_elements_vidible(True)
        self.state = 0
        pg.mixer.music.unpause()


    def set_elements_vidible(self, value):
        "Sets visible of all game elements"
        for element in self.elements:
            element.visible = value


    def toggle_autopilot(self):
        "Toggles autopilot var"
        self.autopilot = not self.autopilot


    def on_collision(self, arbiter: pm.arbiter.Arbiter, space: pm.Space, data):
        "Removes grid body on collision"
        space.remove(arbiter.shapes[1])
        self.grid.remove_shape(arbiter.shapes[1])
        self.master.play(self.sounds[f"Jump{randint(1, 2)}"])
        return True


    def run(self):
        "Runs main cycle"
        running = True

        self.state = 0
        self.states = ["MENU", "PREPARATION", "PLAYING", "DIED", "WINNED"]

        pg.mixer.music.play(-1)
        while running:
            delta = self.clock.tick(self.FPS) / 1000.0
            fps = round(self.clock.get_fps())


            if self.state:
                pg.mouse.set_visible(False)
            else:
                pg.mouse.set_visible(True)
            keys = pg.key.get_pressed()


            "Pygame events"
            #Getting all pygame events
            for event in pg.event.get():


                #Adding pygame GUI events to other
                self.manager.process_events(event)


                #Catching on exit event
                if event.type == pg.QUIT:
                    running = False


                #Catching on key down event
                if event.type == pg.KEYDOWN:

                    #Toggle debug
                    if event.key == pg.K_F3:
                        self.debug = not self.debug

                    #Throw ball
                    if self.state == 1 and event.key == pg.K_SPACE:
                        self.ball_speed = [vel * 15 for vel in self.ball_start_velocity]
                        self.ball.body.velocity = self.ball_speed
                        self.state = 2

                    #End current level
                    if self.state and event.key == pg.K_ESCAPE:
                        self.end_level()


                #Catching timer end user event
                if event.type == self.TIMEREVENT:
                    self.end_level()


                #Catching pygame GUI on button press event
                if event.type == pggui.UI_BUTTON_PRESSED:

                    #Start button
                    if event.ui_element == self.start_btn:
                        self.new_player((250, 15), 750, (255, ) * 4, self.space)
                        self.new_ball(10, (self.player.body.position[0],
                                           self.player.body.position[1] - 100), (255, 0, 0, 255), self.space)
                        self.new_grid((self.size[0], self.size[1] / 2), (8, 4), self.space)
                        self.set_elements_vidible(False)
                        self.state = 1
                        pg.mixer.music.pause()
                        self.master.play(self.sounds["GameStart"])

                    #Exit button
                    if event.ui_element == self.exit_btn:
                        self.master.play(self.sounds["GameExit"])
                        pg.time.delay(220)
                        running = False
                        
                if event.type == pggui.UI_HORIZONTAL_SLIDER_MOVED:
                    if event.ui_element == self.volume_sldr:
                        pg.mixer.music.set_volume(event.value / 100)
                        self.master.set_volume(event.value / 100)


            "Key bindings"
            if self.state:

                #Left
                if keys[pg.K_a] or keys[pg.K_LEFT]:
                    if self.state == 1 and self.angle < 135:
                        self.angle += 100 * delta
                    if self.state == 2 and self.player.body.position[0] - self.player.rect.size[0] / 2 > 0:
                        self.player.body.velocity = (-self.player_speed, 0)
                    else: self.player.body.velocity = (0, 0)

                #Right
                elif keys[pg.K_d] or keys[pg.K_RIGHT]:
                    if self.state == 1 and self.angle > 45:
                        self.angle -= 100 * delta
                    if self.state == 2 and self.player.body.position[0] + self.player.rect.size[0] / 2 < self.size[0]:
                        self.player.body.velocity = (self.player_speed, 0)
                    else:
                        self.player.body.velocity = (0, 0)

                #No pressed keys
                else:
                    if self.state == 2:
                        self.player.body.velocity = (0, 0)


            "Autopilot"
            if self.autopilot:
                self.player.body.position = (self.ball.body.position[0], self.player.body.position[1])


            "Limitations"
            #Locking the speed of the ball
            if self.state == 2:
                "Game states"
                #Game over when the ball crosses the length of the screen + the radius of the ball
                if self.ball.body.position[1] > self.size[1]:
                    pg.time.set_timer(self.TIMEREVENT, 2500, 1)
                    self.master.play(self.sounds["PlayerDie"])
                    self.state = 3

                #Game win when ball breaks all grid bodies
                if not len(self.grid.get_shapes()):
                    pg.time.set_timer(self.TIMEREVENT, 2500)
                    self.master.play(self.sounds["PlayerWin"])
                    self.state = 4


            "Update"
            #UIManager update
            self.manager.update(delta)

            if self.state == 2:
                #Pymunk space update
                self.space.step(delta)

            #Pygame screen update
            self.screen.fill("#070707")


            "Draw"
            #Drawing manager GUI
            if not self.state:
                self.manager.draw_ui(self.screen)

            if self.state == 1:
                #Drawing arrow
                self.draw_arrow(self.ball.body.position, self.angle)

                #Setting start ball velocity | direction
                self.ball_start_velocity = (self.end_x - self.ball.body.position[0],
                                            self.end_y - self.ball.body.position[1])


            if self.state:
                #Drawing player
                self.player.draw(self.screen)

                #Drawing ball
                self.ball.draw(self.screen)

                #Drawing grid
                self.grid.draw(self.screen)

                if self.state == 3:
                    #Drawing game over text
                    text = self.header_font.render("Game over!", True, "#FFFFFF")
                    self.screen.blit(text, (self.size[0] / 2 - text.width / 2, self.size[1] / 2 - text.height / 2))

                if self.state == 4:
                    #Drawing game win text
                    text = self.header_font.render("Game win!", True, "#FFFFFF")
                    self.screen.blit(text, (self.size[0] / 2 - text.width / 2, self.size[1] / 2 - text.height / 2))

            else:
                #Drawing game title
                self.screen.blit(self.header_font.render("PingPY", True, "#FFFFFF"), (10, -30))


            "Debug"
            if self.debug:
                if self.state:
                    #Drawing pymunk debug draw
                    self.space.debug_draw(self.options)

                #Drawing current fps
                self.screen.blit(self.debug_font.render(f"{str(fps)} fps", True, "#FFFFFF", "#000000"), (0, 0))

                #Drawing the value of the state var
                self.screen.blit(self.debug_font.render(f"state: {self.states[self.state]}", True, "#FFFFFF", "#000000"), (0, 24))


            #Displaying on window
            pg.display.update()
        pg.quit()


#Launching the game
if __name__ == "__main__":
    game = Game(size=(0, 0), flags=pg.NOFRAME, caption="PingPY", theme_path="_internal\\theme.json")
    game.run()