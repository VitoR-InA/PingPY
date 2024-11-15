from _internal.classes.Bodies import Ball, Player, Wall
from _internal.classes.Grid import Grid

from datetime import datetime

from math import sin, cos, radians

import pygame as pg
import pygame_gui as pggui
import pymunk as pm

from pygame_gui import UIManager
from pygame_gui.elements import UIButton
from pymunk import pygame_util as pgu

from random import randint

from typing import Tuple


def get_sign(num: int | float):
    """
    Returns:
        str: sign of given number
    """
    return "-" if num < 0 else ""


class Game:
    def __init__(self,
                 size: Tuple[int, int],
                 flags: int = 0,
                 caption: str = "Window",
                 fps: int = 60):
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
        self.manager = UIManager(self.size)

        #Window title
        pg.display.set_caption(caption)
        
        
        "Sounds"
        #Bodies sound channels
        self.ball_channel = pg.mixer.Channel(1)
        self.ball_channel.set_volume(0.5)
        self.player_channel = pg.mixer.Channel(2)
        self.player_channel.set_volume(0.5)
        pg.mixer.music.load("_internal\\music\\Music.wav")
        
        #Sounds var
        self.sounds = {}


        "Pymunk init"
        #Pymunk space setup
        pgu.positive_y_is_up = False
        self.space = pm.Space()

        #Defining on collision handler
        collision_handler = self.space.add_collision_handler(1, 2)
        collision_handler.begin = self.on_collision

        #Defining debug draw options
        self.options = pgu.DrawOptions(self.screen)
        self.debug = False


        "Pymunk bodies"
        #Defining ball
        self.ball_radius = 10
        self.ball = Ball(1, (0, 0), self.ball_radius, (255, 0, 0, 255), self.space)
        self.ball_start_velocity = None
        self.ball_speed = (0, 0)
        self.angle = 90
        self.sounds["Jump1"] = pg.mixer.Sound("_internal\\music\\Jump.wav")
        self.sounds["Jump2"] = pg.mixer.Sound("_internal\\music\\Jump2.wav")

        #Defining player
        self.player = Player(pg.Rect(self.size[0] / 2, self.size[1] - 50, 150, 15), (255, 255, 255, 255), self.space)
        self.autopilot = False
        self.player_speed = 0
        self.state = 0
        self.sounds["PlayerWin"] = pg.mixer.Sound("_internal\\music\\playerWin.wav")
        self.sounds["PlayerDie"] = pg.mixer.Sound("_internal\\music\\PlayerDie.wav")
        self.sounds["GameStart"] = pg.mixer.Sound("_internal\\music\\GameStart.wav")
        self.sounds["GameExit"] = pg.mixer.Sound("_internal\\music\\GameExit.wav")

        #Defining walls
        wall_size = 15
        Wall((0, -wall_size), (self.size[0], -wall_size), wall_size, self.space)
        Wall((-wall_size, 0), (-wall_size, self.size[1]), wall_size, self.space)
        Wall((self.size[0] + wall_size - 1, 0), (self.size[0] + wall_size - 1, self.size[1]), wall_size, self.space)


        "GUI"
        self.elements = []
        
        #Defining start button
        self.start_btn = UIButton(pg.Rect((self.size[0] / 2 - 140, self.size[1] / 2 - 40), (280, 80)), "Start", self.manager)
        self.elements.append(self.start_btn)
        
        #Defining exit button
        self.exit_btn = UIButton(pg.Rect((self.size[0] / 2 - 140, self.size[1] / 2 - 40 + 100), (280, 80)), "Exit", self.manager)
        self.elements.append(self.exit_btn)
        
        #Defining autopilot toggle button
        self.autopilot_btn = UIButton(pg.Rect((self.size[0] - 290, self.size[1] - 90), (280, 80)), f"Autopilot: {'on' if self.autopilot else 'off'}", self.manager)
        self.elements.append(self.autopilot_btn)


        "Fonts"
        #Defining debug font
        self.debug_font = pg.Font(None, 30)

        #Defining header font
        self.header_font = pg.Font(None, 170)


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


    def new_level(self,
                 start_ball_position: Tuple[float, float],
                 ball_speed: Tuple[float, float],
                 player_speed: float,
                 grid_bodies_count: Tuple[int, int]):
        """
        Creates a grid of bodies, defines all necessary variables

        Args:
            start_ball_position (Tuple[float, float]): defines ball position
            ball_speed (Tuple[float, float]): defines ball constant speed
            player_speed (float): defines player constant speed
            grid_bodies_count (Tuple[int, int]): defines number of grid bodies
        """
        self.ball.body.position = start_ball_position
        self.ball_speed = ball_speed
        self.player_speed = player_speed
        self.grid = Grid(self.space, pg.Rect(0, 0, self.size[0], self.size[1] / 2.5), grid_bodies_count)
        self.set_elements_vidible(False)
        self.state = 1
        pg.mixer.music.pause()


    def end_level(self):
        "Stops current level"
        for shape in self.grid.get_shapes():
            self.space.remove(shape)
            self.grid.remove_shape(shape)
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
        self.ball_channel.play(self.sounds[f"Jump{randint(1, 2)}"])
        return True


    def run(self):
        "Runs main cycle"
        running = True
        pg.mixer.music.play(-1)
        while running:
            delta = self.clock.tick(self.FPS) / 1000.0
            fps = round(self.clock.get_fps())


            if self.state:
                pg.mouse.set_visible(False)
            else:
                pg.mouse.set_visible(True)
            keys = pg.key.get_pressed()


            """Pygame events"""
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
                        speed = (self.ball_start_velocity[0] * 15, self.ball_start_velocity[1] * 15)
                        self.ball_speed = speed
                        self.ball.body.velocity = speed
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
                        self.player.body.position = (self.size[0] / 2, self.size[1] - 50)
                        self.angle = 90
                        self.new_level((self.player.body.position[0], self.player.body.position[1] - 100), (0, 0), 0, (16, 8))
                        self.player_channel.play(self.sounds["GameStart"])

                    #Exit button
                    if event.ui_element == self.exit_btn:
                        self.player_channel.play(self.sounds["GameExit"])
                        pg.time.delay(220)
                        running = False

                    if event.ui_element == self.autopilot_btn:
                        self.toggle_autopilot()
                        self.autopilot_btn.set_text(f"Autopilot: {'on' if self.autopilot else 'off'}")


            "Key bindings"
            if self.state:

                #Left
                if (keys[pg.K_a] or keys[pg.K_LEFT]):
                    if self.state == 1 and self.angle < 165:
                        self.angle += 3
                    if self.state == 2 and not self.autopilot:
                        self.player.body.velocity = (-self.player_speed, 0)

                #Right
                elif (keys[pg.K_d] or keys[pg.K_RIGHT]):
                    if self.state == 1 and self.angle > 15:
                        self.angle -= 3
                    if self.state == 2 and not self.autopilot:
                        self.player.body.velocity = (self.player_speed, 0)

                #No pressed keys
                else:
                    if self.state == 2:
                        self.player.body.velocity = (0, 0)


            "Autopilot"
            if self.autopilot:
                self.player.body.position = (self.ball.body.position[0], self.player.body.position[1])


            "Limitations"
            #Limiting the player's movement
            player_x_limit = max(min(self.player.body.position[0], self.size[0] - self.player.rect.size[0] / 2), self.player.rect.size[0] / 2)
            self.player.body.position = (player_x_limit, self.player.body.position[1])

            #Locking the speed of the ball
            if self.state == 2:
                self.ball.body.velocity = (float(f"{get_sign(self.ball.body.velocity[0])}{abs(self.ball_speed[0])}"),
                                           float(f"{get_sign(self.ball.body.velocity[1])}{abs(self.ball_speed[1])}"))


                "Game states"
                #Game over when the ball crosses the length of the screen + the radius of the ball
                if self.ball.body.position[1] > self.size[1] + self.ball_radius:
                    pg.time.set_timer(self.TIMEREVENT, 2500)
                    self.player_channel.play(self.sounds["PlayerDie"])
                    self.state = 3

                #Game win when ball breaks all grid bodies
                if not len(self.grid.get_shapes()):
                    pg.time.set_timer(self.TIMEREVENT, 2500)
                    self.player_channel.play(self.sounds["PlayerWin"])
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
            self.manager.draw_ui(self.screen)

            if self.state == 1:
                #Drawing arrow
                self.draw_arrow(self.ball.body.position, self.angle)

                #Setting start ball velocity | direction
                self.ball_start_velocity = (self.end_x - self.ball.body.position[0],
                                            self.end_y - self.ball.body.position[1])

                #Setting player speed
                self.player_speed = max(abs(self.ball_start_velocity[0] * 15), abs(self.ball_start_velocity[1] * 15))


            if self.state:
                #Drawing player
                self.player.draw(self.screen)
                
                #Drawing ball
                self.ball.draw(self.screen)
                
                #Drawing grid
                self.grid.draw(self.screen)
                
                if self.state == 3:
                    #Drawing game over text
                    text = self.header_font.render("Game over!", True, "#B0B0B0")
                    self.screen.blit(text, (self.size[0] / 2 - text.width / 2, self.size[1] / 2 - text.height / 2))
                
                if self.state == 4:
                    #Drawing game win text
                    text = self.header_font.render("Game win!", True, "#B0B0B0")
                    self.screen.blit(text, (self.size[0] / 2 - text.width / 2, self.size[1] / 2 - text.height / 2))
                
            else:
                #Drawing game title
                text = self.header_font.render("PingPY", True, "#B0B0B0")
                self.screen.blit(text, (self.size[0] / 2 - text.width / 2, 100))


            "Debug"
            if self.debug:
                if self.state:
                    #Drawing pymunk debug draw
                    self.space.debug_draw(self.options)

                #Drawing current fps
                self.screen.blit(self.debug_font.render(f"{str(fps)} fps", True, "#FFFFFF", "#000000"), (0, 0))

                #Drawing the value of the state var
                self.screen.blit(self.debug_font.render(f"state: {self.state}", True, "#FFFFFF", "#000000"), (0, 25))

                #Drawing the value of the self.player_speed var
                self.screen.blit(self.debug_font.render(f"player speed: {self.player_speed}", True, "#FFFFFF", "#000000"), (0, 50))
                
                #Drawing the value of the self.player.body.position[0] var
                self.screen.blit(self.debug_font.render(f"player position: {self.player.body.position[0]}", True, "#FFFFFF", "#000000"), (0, 75))

                #Drawing the value of the self.ball_speed var
                self.screen.blit(self.debug_font.render(f"ball speed: {self.ball_speed}", True, "#FFFFFF", "#000000"), (0, 100))
                
                #Drawing the value of the self.ball.body.velocity var
                self.screen.blit(self.debug_font.render(f"ball velocity: {self.ball.body.velocity}", True, "#FFFFFF", "#000000"), (0, 125))

                #Drawing the value of the self.ball_speed var
                self.screen.blit(self.debug_font.render(f"start ball velocity: {self.ball_start_velocity}", True, "#FFFFFF", "#000000"), (0, 150))


            #Displaying on window
            pg.display.update()
        pg.quit()


#Launching the game
if __name__ == "__main__":
    game = Game(size=(0, 0), flags=pg.NOFRAME, caption="PingPY")
    game.run()