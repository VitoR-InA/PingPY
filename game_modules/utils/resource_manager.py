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

    def load(self, resource_path: os.PathLike):
        # Loads selected resource
        with ZipFile(os.path.join(self.resources_path, resource_path)) as zip:

            self.loaded_resource = os.path.join(self.resources_path, f".{os.path.splitext(os.path.basename(zip.filename))[0]}")

            zip.extractall(self.loaded_resource) # Extracts all loaded_resource file data

            if os.name == "nt": os.system(f"attrib +H {self.loaded_resource}") # Hides extracted folder for windows systems

    def has(self, file_path: os.PathLike) -> bool:
        if os.path.exists(os.path.join(self.loaded_resource, file_path)):
            return True
        else: return False

    def get(self, file_path: os.PathLike) -> os.PathLike:
        return os.path.join(self.loaded_resource, file_path)

    def close(self):
        if os.path.exists(self.loaded_resource): shutil.rmtree(self.loaded_resource)