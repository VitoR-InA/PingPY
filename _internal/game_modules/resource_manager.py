import os
import shutil

from zipfile import ZipFile


class ResourceLoader:
    "Simple tool to work with PingPY resources"
    @classmethod
    def load(self, file: os.PathLike):
        with ZipFile(file) as zip:
            self.path = os.path.join(os.path.dirname(zip.filename), f".{os.path.splitext(os.path.basename(zip.filename))[0]}")
            zip.extractall(self.path)
            if os.name == "nt": os.system(f"attrib +H {self.path}")

    @classmethod
    def has(self, section: str, file: str) -> bool:
        if os.path.exists(os.path.join(self.path, section, file)):
            return True
        else: return False

    @classmethod
    def get(self, section: str, file: str) -> os.PathLike:
        return os.path.join(self.path, section, file)

    @classmethod
    def close(self): shutil.rmtree(self.path)