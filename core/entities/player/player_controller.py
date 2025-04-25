from .player import Player
from core import typing


class PlayerController:
    def __init__(self, player: Player):
        self.player = player

    def move_up(self, time_delta: typing.Optional[float] = 1):
        self.player.move_ip((0, -self.player.current_speed * time_delta))

    def move_left(self, time_delta: typing.Optional[float] = 1):
        self.player.move_ip((-self.player.current_speed * time_delta, 0))

    def move_down(self, time_delta: typing.Optional[float] = 1):
        self.player.move_ip((0, self.player.current_speed * time_delta))

    def move_right(self, time_delta: typing.Optional[float] = 1):
        self.player.move_ip((self.player.current_speed * time_delta, 0))