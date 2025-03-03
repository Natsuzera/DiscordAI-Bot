import json
from .load_path import load_json_reader
import imaplib
import email
from email.header import decode_header
from email.utils import parseaddr
from typing import List, Dict
from bs4 import BeautifulSoup
import html2text

class EmailProcessor:
    def __init__(self):
        data = load_json_reader()
        self.EMAIL = data['email']
        self.PASSWORD = data['password']
        self.SENDER_LIST = data['remetentes']
        self.IMAP_SERVER = 'imap.gmail.com'
        self.h = html2text.HTML2Text()
        self.h.ignore_links = False  # Mantém os links
        self.h.ignore_images = True  # Mantém referências a imagens
        self.h.ignore_tables = True  # Mantém as tabelas
        
    def clean_html_content(self, html_content: str) -> str:
        """
        Limpa o conteúdo HTML mantendo a maior parte da estrutura original
        """
        try:
            # Usar BeautifulSoup apenas para parsing inicial
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove apenas scripts e estilos
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Converte para texto mantendo a maior parte da estrutura
            text_content = self.h.handle(str(soup))
            
            # Remove apenas linhas completamente vazias
            text_content = '\n'.join(line for line in text_content.splitlines() if line.strip())
            
            return text_content
            
        except Exception as e:
            print(f"Erro ao limpar HTML: {e}")
            # Em caso de erro, retorna o conteúdo original
            return html_content

    def extract_email_content(self, msg) -> Dict[str, str]:
        """
        Extrai o conteúdo do email, priorizando HTML mas mantendo texto plano como fallback
        """
        content = {
            'text': '',
            'html': '',
            'processed': ''
        }
        
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_maintype() == 'multipart':
                    continue
                if part.get_content_maintype() == 'text':
                    try:
                        body = part.get_payload(decode=True).decode(part.get_content_charset() or 'utf-8')
                        if part.get_content_type() == 'text/plain':
                            content['text'] = body
                        elif part.get_content_type() == 'text/html':
                            content['html'] = body
                    except Exception as e:
                        print(f"Erro ao decodificar parte do email: {e}")
        else:
            try:
                body = msg.get_payload(decode=True).decode(msg.get_content_charset() or 'utf-8')
                if msg.get_content_type() == 'text/plain':
                    content['text'] = body
                elif msg.get_content_type() == 'text/html':
                    content['html'] = body
            except Exception as e:
                print(f"Erro ao decodificar email: {e}")
        
        # Se tiver HTML, processa ele, senão usa o texto plano
        if content['html']:
            content['processed'] = self.clean_html_content(content['html'])
        elif content['text']:
            content['processed'] = content['text']
            
        return content

    def fetch_unread_emails(self) -> List[Dict[str, str]]:
        """
        Busca emails não lidos e retorna seu conteúdo
        """
        email_contents = []
        
        try:
            mail = imaplib.IMAP4_SSL(self.IMAP_SERVER)
            mail.login(self.EMAIL, self.PASSWORD)
            mail.select('inbox')
            
            # Busca apenas emails não lidos
            # Removido filtro por remetente da pesquisa; o filtro ainda é feito abaixo.
            status, messages = mail.search(None, 'UNSEEN')
            
            if status != 'OK' or not messages[0]:
                return []
            
            for email_id in messages[0].split():
                status, data = mail.fetch(email_id, '(RFC822)')
                if status != 'OK':
                    continue
                
                msg = email.message_from_bytes(data[0][1])
                _, sender_email = parseaddr(msg.get('From'))
                
                # Verifica se o remetente está na lista
                if sender_email not in self.SENDER_LIST:
                    continue
                
                content = self.extract_email_content(msg)
                if content['processed']:
                    email_contents.append({
                        'sender': sender_email,
                        'subject': msg.get('Subject'),
                        'content': content['processed']
                    })
                    
        except Exception as e:
            print(f"Erro ao buscar emails: {e}")
            
        finally:
            if 'mail' in locals():
                try:
                    mail.close()
                except:
                    pass
                mail.logout()
                
        return email_contents

if __name__ == '__main__':
    processor = EmailProcessor()
    emails = processor.fetch_unread_emails()
    for idx, email_data in enumerate(emails, 1):
        print(f"\nEmail {idx}:")
        print(f"De: {email_data['sender']}")
        print(f"Assunto: {email_data['subject']}")
        print(f"Conteúdo processado:\n{email_data['content']}\n{'-'*50}")