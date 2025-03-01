from configobj import ConfigObj

import os
import shutil

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
        with ZipFile(file) as zip:
            self.resource = os.path.join(self.resources_path, f".{os.path.splitext(os.path.basename(zip.filename))[0]}")
            zip.extractall(self.resource)
            if os.name == "nt": os.system(f"attrib +H {self.resource}")

    def has(self, path: os.PathLike) -> bool:
        if os.path.exists(os.path.join(self.resource, path)):
            return True
        else: return False

    def get(self, path: os.PathLike) -> os.PathLike:
        return os.path.join(self.resource, path)

    def close(self): shutil.rmtree(self.resource)