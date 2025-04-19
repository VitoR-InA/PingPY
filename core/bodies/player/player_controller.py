from core.bodies.player import Player

from multipledispatch import dispatch
from numbers import Real

import typing


class PlayerController:
    def __init__(self, player: Player):
        self.player = player
        self.player_speed = self.player.get_speed()

    def move_up(self, time_delta: typing.Optional[float] = 1): self.player.move_ip((0, -self.player_speed * time_delta))
    def move_left(self, time_delta: typing.Optional[float] = 1): self.player.move_ip((-self.player_speed * time_delta, 0))
    def move_down(self, time_delta: typing.Optional[float] = 1): self.player.move_ip((0, self.player_speed * time_delta))
    def move_right(self, time_delta: typing.Optional[float] = 1): self.player.move_ip((self.player_speed * time_delta, 0))

    @dispatch()
    def update_speed(self):
        self.player_speed = self.player.get_speed()

    @dispatch(Real)
    def update_speed(self, new_speed: float):
        self.player.set_speed(new_speed)
        self.player_speed = self.player.get_speed()