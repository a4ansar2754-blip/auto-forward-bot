import json
import os

CONFIG_DIR = "configs"

if not os.path.exists(CONFIG_DIR):
    os.makedirs(CONFIG_DIR)

def get_config(user):

    path = f"{CONFIG_DIR}/{user}.json"

    if not os.path.exists(path):

        data = {
            "sources": [],
            "targets": [],
            "keywords": [],
            "replace_link": "",
            "header": "",
            "footer": "",
            "delay": 0,
            "autodelete": 0
        }

        with open(path, "w") as f:
            json.dump(data, f)

        return data

    with open(path) as f:
        return json.load(f)

def save_config(user, data):

    path = f"{CONFIG_DIR}/{user}.json"

    with open(path, "w") as f:
        json.dump(data, f, indent=4)
