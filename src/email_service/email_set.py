import json
from load_path import load_json_reader, load_json_write
    
def set_email(email: str):
    data = load_json_reader()
    data['email'] = email
    with open(load_json_write(), 'w') as file:
        json.dump(data, file, indent=4)

def set_password(password: str):
    data = load_json_reader()
    data['password'] = password
    with open(load_json_write(), 'w') as file:
        json.dump(data, file, indent=4)

def set_remetentes(remetentes: list):
    data = load_json_reader()
    data['remetentes'] = remetentes
    with open(load_json_write(), 'w') as file:
        json.dump(data, file, indent=4)







    

