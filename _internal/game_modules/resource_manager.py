from configobj import ConfigObj

import os

from zipfile import ZipFile


class ResourceManager:
    "Simple tool to work with PingPY resources"
    def __init__(self, resources_path: os.PathLike):
        self.resources_path = resources_path
        self.config_obj = ConfigObj(os.path.join(self.resources_path, ".properties"))
        if not self.config_obj.get("chosen_resource"):
            self.config_obj["chosen_resource"] = "default.zip"
        self.config_obj.write()

    def load(self, file: os.PathLike):
        self._zip = ZipFile(file)

    def has(self, path: os.PathLike) -> bool:
        try:
            self._zip.getinfo(path)
            return True
        except KeyError: return False

    def get(self, path: os.PathLike) -> bytes:
        return self._zip.read(path)

    def close(self): self._zip.close()