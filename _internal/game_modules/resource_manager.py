import os
import shutil

from zipfile import ZipFile


class ResourceManager:
    "Simple tool to work with PingPY resources"
    @classmethod
    def load(self, file: os.PathLike):
        with ZipFile(file) as zip:
            self.path = os.path.join(os.path.dirname(zip.filename), f".{os.path.splitext(os.path.basename(zip.filename))[0]}")
            zip.extractall(self.path)
            if os.name == "nt": os.system(f"attrib +H {self.path}")

    @classmethod
    def has(self, path: os.PathLike) -> bool:
        if os.path.exists(os.path.join(self.path, path)):
            return True
        else: return False

    @classmethod
    def get(self, path: os.PathLike) -> os.PathLike:
        return os.path.join(self.path, path)

    @classmethod
    def close(self): shutil.rmtree(self.path)