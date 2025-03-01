from configobj import ConfigObj

import os
import shutil

from zipfile import ZipFile


class ResourceManager:
    "Simple tool to work with PingPY resources"
    def __init__(self, resources_path: os.PathLike):
        self.resources_path = resources_path # Path where will be located all game data

        # Creates resources directory
        if not os.path.exists(self.resources_path):
            os.makedirs(self.resources_path, exist_ok = True)

        # Creates config file in resource directory
        self.config_obj = ConfigObj(os.path.join(self.resources_path, ".properties"))
        if not self.config_obj.get("chosen_resource"):
            self.config_obj["chosen_resource"] = "default.zip"

        self.config_obj.write() # Saves config changes

    def load(self, file: os.PathLike):
        "Extracts all resource data in the same dir with same name, made for compat with pygame_gui"
        with ZipFile(file) as zip:
            self.loaded_resource = os.path.join(self.resources_path, f".{os.path.splitext(os.path.basename(zip.filename))[0]}")

            zip.extractall(self.loaded_resource) # Extracts all loaded_resource file data

            if os.name == "nt": os.system(f"attrib +H {self.loaded_resource}") # Hides extracted folder for windows systems

    def has(self, path: os.PathLike) -> bool:
        if os.path.exists(os.path.join(self.loaded_resource, path)):
            return True
        else: return False

    def get(self, path: os.PathLike) -> os.PathLike:
        return os.path.join(self.loaded_resource, path)

    def read(self, path: os.PathLike) -> bytes:
        return open(os.path.join(self.loaded_resource, path), "rb")

    def close(self): shutil.rmtree(self.loaded_resource)