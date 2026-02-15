import os, json
from pathlib import Path

def save_json(path,data):
    os.makedirs(os.path.dirname(path),exist_ok=True)
    with open(path,"w",encoding="utf-8") as f: json.dump(data,f,indent=4)

def load_json(path):
    try: return json.load(open(path,"r",encoding="utf-8"))
    except: return None

def load_params():
    # Load from the parameter directory relative to this file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    params_path = os.path.join(current_dir, "parameter", "params.json")
    return load_json(params_path)

