import json


def read_json(path="data/key.json"):
    with open(path, "r", encoding='utf-8') as json_file:
        return json.load(json_file)
