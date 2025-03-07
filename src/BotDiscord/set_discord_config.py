import os
import sys
import json

# Ajusta o path para poder importar módulos do diretório pai
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from utils.load_path import load_json_reader, load_json_text_reader, load_json_write, load_json_text_write

def set_discord_credentials(id_servidor : int, channel_agendamento_id : int, channel_welcome_id : int, discord_token : str):
    """
    Salva as credenciais do Discord em um arquivo JSON
    """
    data = {
        "id_servidor": id_servidor,
        "channel_agendamento_id": channel_agendamento_id,
        "channel_welcome_id": channel_welcome_id,
        "discord_token": discord_token
    }
    
    with open(load_json_write("discord-credentials-example"), "w") as file:
        json.dump(data, file, indent=4)


