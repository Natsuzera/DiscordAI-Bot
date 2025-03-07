import os
import sys

# Ajusta o path para poder importar módulos do diretório pai
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from utils.load_path import load_json_reader, load_json_text_reader

def get_discord_credentials():
    credenciais = load_json_reader('discord-credentials')
    return credenciais

def get_discord_texts() -> dict:
    textos = load_json_text_reader('bot_texts')
    return textos


def get_discord_comandos() -> dict:
    comandos = load_json_text_reader('comandos')
    return comandos


