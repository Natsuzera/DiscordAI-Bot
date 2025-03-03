import ollama
import torch
import os
import sys
from typing import Optional

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from email_service.email_extract import EmailProcessor

def process_unread_email_response(model_name: str = 'llama3.2:3b') -> str:
    """
    Processa o primeiro email não lido e extrai o código de acesso usando LLM.
    Retorna a resposta da LLM como uma string.
    Caso não haja emails não lidos ou ocorra algum erro, retorna uma mensagem informativa.
    """
    # Configura o dispositivo (GPU/CPU)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Usando dispositivo: {device}")
    
    try:
        email_processor = EmailProcessor()
        emails = email_processor.fetch_unread_emails()
        
        if not emails:
            return "Nenhum email não lido encontrado."
            
        # Processa apenas o primeiro email encontrado (para integração inicial)
        email_data = emails[0]
        print(f"Processando email de: {email_data['sender']} - Assunto: {email_data['subject']}")
        
        # Define o prompt para extrair o código de acesso
        prompt = (
            "Extraia exclusivamente o código de acesso numérico ou o link de acesso do seguinte conteúdo HTML. "
            "A resposta deve conter apenas esse valor, sem qualquer explicação, formatação, rótulo, texto adicional ou caracteres extras. "
            "Se o conteúdo for um email da Netflix, retorne apenas o link de acesso, que geralmente segue o formato: "
            "'https://www.netflix.com/account/travel/...'. "
            "Se for de qualquer outro serviço, retorne apenas o código numérico de acesso (exemplo: '876962'). "
            "Não inclua quebras de linha, espaços extras ou qualquer outro caractere além do código ou link. "
            "Se houver múltiplos códigos ou links, retorne apenas o primeiro encontrado. "
            "O resultado deve ser exatamente o código ou link, sem nada mais. "
            f"Conteúdo HTML: {email_data['content']}"
        )

        try:
            response = ollama.chat(
                model=model_name,
                messages=[{'role': 'user', 'content': prompt}]
            )
            print(response.message.content.strip())
            return response.message.content.strip()
        except Exception as e:
            return f"Erro ao processar com LLM: {e}"
            
    except Exception as e:
        return f"Erro durante o processamento do email: {e}"
    finally:
        # Limpa cache da GPU se aplicável
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    
def process_chatbot_message(message: str, model_name: str = 'llama3.2:3b') -> str:
    """
    Processa a mensagem do chatbot usando LLM local
    """

    prompt = f"Responda em português do brazil a seguinte mensagem: {message}"

    try:
        response = ollama.chat(
            model=model_name,
            messages=[{
                'role': 'user',
                'content': prompt
            }]
        )
        print(response.message.content.strip())
        return response.message.content.strip()
        
    except Exception as e:
        print(f"Erro ao processar com LLM: {e}")
        return "Desculpe, não consegui entender o que você disse"
    