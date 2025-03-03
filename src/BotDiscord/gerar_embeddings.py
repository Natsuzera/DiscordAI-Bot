from typing import List
import chromadb
import ollama

# Inicializar o cliente ChromaDB
cliente = chromadb.PersistentClient(path="data/chroma.db")

# Verificar se a coleção já existe e deletá-la se necessário
try:
    collection = cliente.get_collection("embeddings")
    cliente.delete_collection("embeddings")
    print("Coleção antiga deletada.")
except Exception as e:
    print("Nenhuma coleção encontrada para deletar. Criando uma nova.")

collection = cliente.create_collection("embeddings")  # Cria uma nova coleção

# Função para gerar embedding usando Ollama
def generate_embedding(text: str) -> List[float]:
    response = ollama.embeddings(model='nomic-embed-text', prompt=text)
    return response['embedding']

# Função para quebrar o texto em partes
def quebrar_texto(texto: str, tamanho: int = 210, sobrepor: int = 40, min_tamanho_ultimo: int = 200) -> List[str]:
    if tamanho <= sobrepor:
        raise ValueError("O tamanho deve ser maior que o sobrepor")
    
    partes = []
    inicio = 0
    while inicio < len(texto):
        final = inicio + tamanho
        if final >= len(texto):
            # Verificar se a última parte é muito pequena
            if len(texto) - inicio < min_tamanho_ultimo and len(partes) > 0:
                # Ajustar para pegar mais texto da parte anterior
                ultimo_inicio = max(0, len(texto) - tamanho)
                partes[-1] = texto[ultimo_inicio:len(texto)]
            else:
                partes.append(texto[inicio:len(texto)])
            break
        partes.append(texto[inicio:final])
        inicio += tamanho - sobrepor
    
    return partes

# Ler o texto do arquivo
with open("src/BotDiscord/texto.txt", "r") as file:
    texto = file.read()

# Quebrar o texto em partes
partes = quebrar_texto(texto)

# Gerar embeddings para cada parte usando Ollama
embeddings = [generate_embedding(parte) for parte in partes]

# Adicionar os embeddings à coleção no ChromaDB
collection.add(embeddings=embeddings, documents=partes, ids=[str(i) for i in range(len(partes))])

# Verificar se os dados foram adicionados
print(f"Total de documentos adicionados: {collection.count()}")

# (Opcional) Imprimir as partes para verificar
for i, parte in enumerate(partes):
    print(f"Parte {i+1}:\n{parte}\n")
    print("-" * 50)