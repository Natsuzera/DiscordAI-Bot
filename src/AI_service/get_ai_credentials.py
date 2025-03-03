import os
import sys

# Ajusta o path para poder importar módulos do diretório pai
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from utils.load_path import load_json_reader

def get_gemini_credentials():
    credenciais = load_json_reader('gemini-config')

    return credenciais