import os
import sys
import google.generativeai as genai
from typing import List
from PIL import Image
import fitz
import datetime
from .get_ai_credentials import get_gemini_credentials, get_gemini_prompts

credentials = get_gemini_credentials()
text_prompts = get_gemini_prompts()

# Configuração do Gemini
genai.configure(api_key=credentials["gemini-token"])

# Configuração do modelo
generation_config = {
    "temperature": 0.7,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
  model_name=credentials["gemini-model"],
  generation_config=generation_config,
)

# Adiciona diretório pai ao path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from email_service.email_extract import EmailProcessor

def process_unread_email_response() -> str:
    """
    Processa o primeiro email não lido e extrai o código de acesso usando Gemini.
    Retorna a resposta como string ou mensagem de erro.
    """
    try:
        email_processor = EmailProcessor()
        emails = email_processor.fetch_unread_emails()
        
        if not emails:
            return "Nenhum email não lido encontrado."
            
        email_data = emails[0]
        print(f"Processando email de: {email_data['sender']} - Assunto: {email_data['subject']}")
        
        prompt = text_prompts["email_prompt"]
        prompt = prompt.replace("{content}", email_data["content"])

        try:
            chat_session = model.start_chat(history=[])
            response = chat_session.send_message(prompt)
            resultado = response.text.strip()
            print(resultado)
            return resultado
        except Exception as e:
            return f"Erro ao processar com Gemini: {e}"
            
    except Exception as e:
        return f"Erro durante o processamento do email: {e}"

def process_chatbot_message(message: str, cargo: str, contexto: str) -> str:
    """
    Processa mensagens do chatbot usando Gemini.
    Retorna resposta em português ou mensagem de erro.
    """

    prompt = text_prompts["prompt_chatbot"]
    prompt = prompt.replace("{cargo}", cargo).replace("{message}", message).replace("{contexto}", contexto)
    
    try:
        chat_session = model.start_chat(history=[])
        response = chat_session.send_message(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Erro ao processar com Gemini: {e}")
        return "Desculpe, não consegui entender o que você disse"

def process_pagamento(path: str, cargo: str) -> str:
    """
    Processa o comprovante de pagamento usando Gemini.
    Retorna a resposta em português ou mensagem de erro.
    """
    try:

        # Verifica se o arquivo é um PDF e converte para imagem
        if path.endswith(".pdf"):
            pdf = fitz.open(path)
            page = pdf.load_page(0)
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        else:
            img = Image.open(path)

        mes_atual = datetime.datetime.now().month
        meses_portugues = [
            "janeiro", "fevereiro", "março", "abril", "maio", "junho",
            "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"
        ]
        mes_atual = meses_portugues[mes_atual - 1]

        prompt = text_prompts["prompt_anexo"]
        prompt = prompt.replace("{cargo}", cargo).replace("{mes_atual}", mes_atual)

        # Inicia uma sessão de chat e envia a imagem com o prompt
        chat_session = model.start_chat(history=[])
        response = chat_session.send_message([prompt, img])
        
        # Retorna a resposta gerada pelo Gemini
        return response.text.strip()
    
    except Exception as e:
        return f"Erro ao processar com Gemini: {e}"
    
