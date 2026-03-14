import json
import os

CONFIG_FOLDER = "configs"

def get_config(user):

    path = f"{CONFIG_FOLDER}/{user}.json"

    if not os.path.exists(path):

        data = {
            "sources": {},
            "targets": {}
        }

        with open(path, "w") as f:
            json.dump(data, f)

        return data

    with open(path) as f:
        return json.load(f)


def save_config(user, data):

    path = f"{CONFIG_FOLDER}/{user}.json"

    with open(path, "w") as f:
        json.dump(data, f)
