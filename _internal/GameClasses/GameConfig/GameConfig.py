from configparser import ConfigParser


class GameConfig(ConfigParser):
    def __init__(self, initial_file = "Ping.ini"):
        super().__init__()
        self.read(initial_file)

    def save_volume(self, volume: float):
        if not self.has_section("GAME"):
            self.add_section("GAME")
        self.set("GAME", str(volume))

    def save_player(self, player_obj):
        