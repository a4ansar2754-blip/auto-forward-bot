import json
import os

os.makedirs("configs",exist_ok=True)

def get_config(user):

    file=f"configs/{user}.json"

    if not os.path.exists(file):

        data={
            "sources":{},
            "targets":{}
        }

        with open(file,"w") as f:
            json.dump(data,f)

        return data

    with open(file) as f:
        return json.load(f)

def save_config(user,data):

    file=f"configs/{user}.json"

    with open(file,"w") as f:
        json.dump(data,f)
