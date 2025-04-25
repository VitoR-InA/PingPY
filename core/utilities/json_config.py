import json

from multipledispatch import dispatch

import os
import typing


class JsonConfig:
    dump_parameters = {"indent": 4, "sort_keys": True}
    def __init__(self, config_path: os.PathLike):
        self.file_path = config_path
        if not os.path.exists(self.file_path):
            os.makedirs(os.path.dirname(self.file_path), exist_ok = True)
            with open(self.file_path, "w") as json_file:
                json.dump({}, json_file, **self.dump_parameters)

    @classmethod
    def merge(self, a: dict, b: dict):
        merged_dict = {}
        for key in a.keys() | b.keys():
            if key in a and key in b:
                merged_dict[key] = self.merge(a[key], b[key])
            else: merged_dict[key] = b[key] if key in b else a[key]
        return merged_dict

    @classmethod
    def set_in_dict(self, a: dict, full_path: str, value):
        splitted_path = full_path.split(".")

        current_key = splitted_path[0]
        if len(splitted_path) == 1: a[current_key] = value
        else:
            if current_key not in a\
                or not isinstance(a.get(current_key), dict): a[current_key] = {}
            self.set_in_dict(a[current_key], ".".join(splitted_path[1:]), value)

    @classmethod
    def get_in_dict(self, a: dict, full_path: str):
        splitted_path = full_path.split(".")

        if not splitted_path or (not splitted_path and type(a) is dict):
            return a

        current_key = splitted_path[0]
        if current_key in a:
            next_value = a.get(current_key)
            if len(splitted_path) == 1: return next_value
            return self.get_in_dict(next_value, ".".join(splitted_path[1:]))
        return None

    @dispatch(str, object)
    def set(self, full_path: typing.Optional[str], value):
        with open(self.file_path, "r+") as json_file:
            loaded_dict = json.load(json_file)
            json_file.seek(0); json_file.truncate(0)
            self.set_in_dict(loaded_dict, full_path, value)
            json.dump(loaded_dict, json_file, **self.dump_parameters)

    @dispatch(str, str, object)
    def set(self, path: typing.Optional[str], key: str, value):
        self.set(f"{path}.{key}", value)

    @dispatch(str)
    def has(self, full_path: str):
        if self.get(full_path): return True
        else: return False

    @dispatch(str, str)
    def has(self, path: typing.Optional[str], key: str):
        return self.has(f"{path}.{key}")

    @dispatch(type(None), str)
    def has(self, path: typing.Optional[str], key: str):
        return self.has(key)

    @dispatch(str)
    def get(self, full_path: str):
        with open(self.file_path, "r+") as json_file:
            loaded_dict = json.load(json_file)
            return self.get_in_dict(loaded_dict, full_path)

    @dispatch(str, str)
    def get(self, path: typing.Optional[str], key: str):
        return self.get(f"{path}.{key}")

    @dispatch(type(None), str)
    def get(self, path: typing.Optional[str], key: str):
        return self.get(key)