import json
import os


def load_json_reader() -> dict:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_dir, '..', '..', 'config/email.json')

    with open(json_path, 'r') as file:
        return json.load(file)
    
def load_json_write() -> str:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_dir, '..', '..', 'config/email.json')

    return json_path