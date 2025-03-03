import chromadb
import ollama

def gerar_input_embeddings(texto: str) -> str:
    # Inicializar o cliente ChromaDB persistente
    cliente = chromadb.PersistentClient(path="data/chroma.db")
    collection = cliente.get_collection("embeddings")
    
    # Verificar se a coleção contém dados
    total_documentos = collection.count()
    print(f"Total de documentos na coleção: {total_documentos}")
    if total_documentos == 0:
        raise ValueError("A coleção 'embeddings' está vazia. Adicione dados antes de fazer a consulta.")
    
    # Gerar embedding do texto de consulta usando Ollama
    embedding_consulta = ollama.embeddings(model='nomic-embed-text', prompt=texto)['embedding']
    
    # Realizar a consulta usando o embedding gerado
    resultados = collection.query(query_embeddings=[embedding_consulta], n_results=2)
    
    # Verificar o conteúdo retornado pela consulta
    #print("Resultados da consulta:", resultados)
    
    # Verificar se documentos foram retornados
    if resultados["documents"] is None or len(resultados["documents"][0]) < 2:
        raise ValueError("Nenhum documento encontrado. Verifique se os documentos foram adicionados à coleção.")
    
    # Recuperar os documentos correspondentes aos embeddings mais similares
    documentos = resultados["documents"][0]
    
    # Concatenar os dois documentos mais similares com um espaço entre eles
    conteudo = f"Contexto recuperado:\n\nDocumento 1:\n{documentos[0]}\n\nDocumento 2:\n{documentos[1]}"
    
    return conteudo
