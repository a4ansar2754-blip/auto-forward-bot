import json
import os

def get_config(user_id):

    path = f"configs/{user_id}.json"

    if not os.path.exists(path):

        data = {
            "sources":{},
            "targets":{},
            "settings":{
                "forward":True,
                "media":True,
                "remove_links":False,
                "remove_username":False,
                "auto_delete":False,
                "replace_link":"",
                "replace_words":{},
                "blacklist":[]
            }
        }

        with open(path,"w") as f:
            json.dump(data,f,indent=2)

    with open(path) as f:
        return json.load(f)


def save_config(user_id,data):

    with open(f"configs/{user_id}.json","w") as f:
        json.dump(data,f,indent=2)
