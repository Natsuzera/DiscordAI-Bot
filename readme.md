# Discord Multifuncional Bot

Este projeto é um bot para Discord em desenvolvimento que integra diversas funcionalidades em um único sistema, oferecendo flexibilidade e facilidade de manutenção. O bot foi projetado para ser adaptável, possibilitando futuras expansões para outros usos.

## Funcionalidades

- **Consulta de E-mails:**  
  Permite a consulta de e-mails diretamente pelo Discord, facilitando o monitoramento e a gestão das mensagens.

- **Chatbot com RAG + LLM:**  
  Utiliza a técnica de RAG (Retrieval Augmented Generation) combinada com um modelo de linguagem (LLM) para interpretar e responder comandos de forma dinâmica.  
  - **Flexibilidade:** Ao invés de criar múltiplos comandos com linhas de código separadas, toda a lógica de comandos é armazenada em um arquivo de texto ou banco de dados contendo descrições e detalhes.  
  - **Atualizações Dinâmicas:** Com o uso de embeddings, qualquer atualização nesse arquivo automaticamente adiciona ou modifica comandos, permitindo respostas precisas sem a necessidade de alterações no código.
  - **Arquivo de Embeddings:** Os comandos e descrições são armazenados no arquivo `src/BotDiscord/texto.txt`, que é utilizado para gerar os embeddings que alimentam o chatbot.

- **Envio de Comprovantes de Pagamentos:**  
  Automatiza o envio de comprovantes de pagamentos, agilizando processos e integrando essa funcionalidade diretamente no Discord.

## Como Funciona

O bot integra diferentes módulos que se comunicam para oferecer uma experiência única:
- **RAG e LLM:** Permitem que o bot interprete a intenção do usuário e forneça respostas adequadas sem depender de comandos rígidos e predefinidos.
- **Armazenamento Dinâmico de Comandos:** Todos os comandos e descrições ficam em um arquivo ou banco de dados, o que facilita a manutenção e atualização do sistema.
- **Flexibilidade de Uso:** Apesar de atualmente estar configurado para trabalhar com LLMs online, existe a possibilidade de utilizar um modelo local, de acordo com as necessidades e recursos disponíveis.

## Design do Sistema

A seguir, um exemplo do design do sistema que ilustra a arquitetura do projeto:

![System Designer](https://raw.githubusercontent.com/Natsuzera/DiscordAI-Bot/master/imagens/ragbotsystem.png)

*Obs.: Substitua "caminho/para/sua-imagem.png" pelo caminho correto da imagem do seu designer de sistema.*

## Configuração do Projeto

Antes de executar o bot, certifique-se de configurar os seguintes arquivos (não se esqueça de adicionar estes arquivos ao seu `.gitignore` para proteger dados sensíveis):

- **`discord-credentials.json`**: Contém as credenciais para acesso ao Discord.  
  > *Exemplo de template:* `discord-credentials.example.json`

- **`email.json`**: Configurações para a consulta de e-mails, incluindo autenticação e remetentes.  
  > *Exemplo de template:* `email.example.json`

- **`gemini-config.json`**: Configurações do LLM, como token e modelo a ser utilizado.  
  > *Exemplo de template:* `gemini-config.example.json`

Recomenda-se criar cópias dos arquivos de exemplo com os nomes corretos e inserir as informações necessárias.

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/seu-repositorio.git
```

2. Acesse o diretório do projeto:
```bash
cd seu-repositorio
```

3. Instale as dependências (certifique-se de ter o ambiente configurado conforme as instruções do seu projeto):
```bash
pip install -r requirements.txt
```

## Uso

Por enquanto, para executar o bot, utilize o seguinte comando, pois o arquivo principal se encontra em `src/BotDiscord/Bot.py`:
```bash
python src/BotDiscord/Bot.py
```

O bot estará online no Discord e pronto para receber comandos conforme a configuração do RAG e LLM.

## Contribuições

Contribuições são bem-vindas! Se você deseja melhorar o projeto ou adicionar novas funcionalidades, sinta-se à vontade para abrir uma issue ou enviar um pull request.

## Licença

Este projeto está licenciado sob a [MIT License](LICENSE).

---

*Este bot está em sua fase inicial e novas funcionalidades serão adicionadas conforme a necessidade. Fique atento às atualizações!*
