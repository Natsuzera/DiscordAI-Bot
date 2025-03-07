import pandas as pd
import os
import sys

# Ajusta o path para poder importar módulos do diretório pai
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)



class SistemaPagamentos:
    def __init__(self, aquivo_pagamentos : str):
        self.pagamentos = pd.DataFrame()
        self.arquivo_pagamentos = f"data/{aquivo_pagamentos}"
        self.carregar_dados()
        

    def carregar_dados(self):
        self.pagamentos = pd.read_csv(self.arquivo_pagamentos)
        
    
    def salvar_dados(self):
        self.pagamentos.to_csv(self.arquivo_pagamentos, index=False)

    def adicionar_pagamento(self, username: str, mes: str) -> str:

        if username not in self.pagamentos["username"].values:
            return f"Usuário {username} não encontrado!"

        try:
            self.pagamentos[mes] = self.pagamentos[mes].astype(str)
            self.pagamentos.loc[self.pagamentos["username"] == username, mes] = "x"
            self.salvar_dados()
            return f"Pagamento de {username} para o mês {mes} adicionado com sucesso!"
        except Exception as e:
            return f"Erro ao adicionar pagamento de {username} para o mês {mes}: {str(e)}"
        
    def verificar_pagamento(self, mes: str) -> str:
        try:
            # Verifica se o DataFrame está vazio
            if self.pagamentos.empty:
                return "Erro: Nenhum usuário cadastrado!"
            
            # Verifica se o mês existe como coluna no DataFrame
            if mes not in self.pagamentos.columns:
                return f"Erro: Mês {mes} não encontrado!"
            
            # Filtra os usuários com pagamento atrasado (sem "x" na coluna do mês)
            atrasados = self.pagamentos[self.pagamentos[mes] != "x"]
            
            # Verifica se há usuários com pagamento atrasado
            if atrasados.empty:
                return f"Todos os pagamentos para o mês {mes} estão em dia!"
            else:
                # Obtém a lista de usernames com pagamento atrasado
                usernames_atrasados = atrasados["username"].tolist()
                # Cria as menções no formato @username
                mencoes = [f"{username}" for username in usernames_atrasados]
                # Monta a mensagem com todas as menções
                mensagem = f"{' '.join(mencoes)}"
                return mensagem
            
        except Exception as e:
            return f"Erro ao verificar pagamentos para o mês {mes}: {str(e)}"
    

    def adicionar_usuario(self, username: str, cargo: str) -> str:
        try:
            novo_usuario = pd.DataFrame({"username": [username], "combo": [cargo]})
            self.pagamentos = pd.concat([self.pagamentos, novo_usuario], ignore_index=True)
            self.salvar_dados()
            return f"Usuário {username} adicionado com sucesso!"
        except Exception as e:
            return f"Erro ao adicionar usuário {username}: {str(e)}"
    
    def remover_usuario(self, username: str) -> str:
        try:
            self.pagamentos = self.pagamentos[self.pagamentos["username"] != username]
            self.salvar_dados()
            return f"Usuário {username} removido com sucesso!"
        except Exception as e:
            return f"Erro ao remover usuário {username}: {str(e)}"
        
        
#Testando
if __name__ == "__main__":
    sistema_pagamentos = SistemaPagamentos("pagamentos.csv")
    print(sistema_pagamentos.verificar_pagamento("Janeiro"))


