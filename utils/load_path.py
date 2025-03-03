import json
import os


def load_json_reader(arquivo: str) -> dict:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_dir, '..', f'config/{arquivo}.json')

    with open(json_path, 'r') as file:
        return json.load(file)
    
def load_json_write(arquivo: str) -> str:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_dir, '..', f'config/{arquivo}.json')

    return json_path
