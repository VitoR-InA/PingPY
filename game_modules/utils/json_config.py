from deepmerge import always_merger

import json

import os
import typing


class JsonConfig:
    dump_parameters = {"indent":4, "sort_keys":True}
    def __init__(self, config_path: os.PathLike):
        self.file_path = config_path
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w") as json_file:
                json.dump({}, json_file, **self.dump_parameters)

    def set(self, section: typing.Optional[str], key_value: typing.Iterable[tuple]):
        with open(self.file_path, "r+") as json_file:
            loaded_json: dict = json.load(json_file)
            json_file.seek(0); json_file.truncate(0)
            merge_dict = dict()
            if section: merge_dict[section] = {}
            for key, value in key_value:
                if section: merge_dict[section][key] = value
                else: merge_dict[key] = value
            json.dump(always_merger.merge(loaded_json, merge_dict), json_file, **self.dump_parameters)

    def has(self, section: typing.Optional[str], key: typing.Optional[str]):
        with open(self.file_path) as json_file:
            loaded_json: dict = json.load(json_file)
            if section: return section in loaded_json.keys() and (key or key in loaded_json[section].keys())
            else: return key in loaded_json.keys()

    def get(self, section: typing.Optional[str], key: str):
        with open(self.file_path) as json_file:
            loaded_json: dict = json.load(json_file)
            return loaded_json[section].get(key) if section else loaded_json.get(key)