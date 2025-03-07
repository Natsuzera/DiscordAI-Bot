import discord
import sys
import os
import asyncio
import datetime
import pytz
from discord import app_commands
from discord.ext import commands, tasks

# Ajusta o path para poder importar módulos do diretório pai
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from embbedings import gerar_input_embeddings
from AI_service.onlineAI import process_chatbot_message, process_unread_email_response, process_pagamento
from get_DiscordConfigs import get_discord_credentials, get_discord_texts, get_discord_comandos
from Pagamentos.pagamentos import SistemaPagamentos

# Define os intents necessários
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

#Pegando as credenciais e configurações do Discord
credentials = get_discord_credentials()
texts = get_discord_texts()
comandos = get_discord_comandos()

# Inicializando a classe de pagamentos
pagamentos = SistemaPagamentos("pagamentos.csv")

meses_portugues = [
            "janeiro", "fevereiro", "marco", "abril", "maio", "junho",
            "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"
            ]

# Cria o cliente do Discord com CommandTree para os slash commands
class ClientBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
    
    async def setup_hook(self):
       
        # ID do servidor onde os comandos serão sincronizados
        guild = discord.Object(id=credentials["id_servidor"])
        self.tree.clear_commands(guild=guild)
        # Copia os comandos globais para o guild específico
        self.tree.copy_global_to(guild=guild)
        # Sincroniza os comandos com o guild para que apareçam instantaneamente
        await self.tree.sync(guild=guild)
        print(f"Comandos sincronizados com a guild {guild.id}")

client = ClientBot()

# Tarefa agendada para enviar mensagem diariamente às 08:00
@tasks.loop(time=datetime.time(hour=15, minute=15, second=0, tzinfo=pytz.timezone('America/Sao_Paulo')))
#@tasks.loop(minutes=1)
async def mensagem_diaria():
    tz = pytz.timezone('America/Sao_Paulo')
    now = datetime.datetime.now(tz)
    # ID do canal de agendamento
    channel = client.get_channel(credentials["channel_agendamento_id"])  # Ex: 123456789012345678
    if now.day in [6, 12]:
        
        if channel:
            
            mes_atual = meses_portugues[now.month - 1]
            atrasados = pagamentos.verificar_pagamento(mes=mes_atual)
            guild_server = channel.guild
            mencoes = []
            for username in atrasados.split():
                print(f"Verificando usuário {username}")
                #pegando o id do usuario no servidor
                member = guild_server.get_member_named(username)
                if member:
                    mencoes.append(member.mention)
                else:
                    print(f"Usuário {username} não encontrado no servidor")
            
            resultado = " ".join(mencoes)
            await channel.send(f"{resultado} verifiquei que o pagamento ainda não foi realizado, a data ideal para pagamento é dia 10")         
    else:
        if channel:
            print("Mensagem diária enviada com sucesso!")
            mensagem = texts["mensagens_usuario"]["mensagem_diaria"]
            await channel.send(mensagem)

        else:
            print("Canal não encontrado!")

# Evento disparado quando o bot estiver pronto
@client.event
async def on_ready():
    print(f'Bot está online como {client.user.name}')
    print('-------------------')
    # Inicia a tarefa agendada
    mensagem_diaria.start()

# Evento disparado quando um novo membro entra no servidor
@client.event
async def on_member_join(member: discord.Member):
    print(f"[EVENTO] Novo membro entrou: {member.name} (ID: {member.id}) na guild {member.guild.name} (ID: {member.guild.id})")
    channel_id = credentials["channel_welcome_id"]  #ID do canal de boas-vindas 
    channel = member.guild.get_channel(channel_id)
    if channel:
        mensagem_boas_vindas = texts["mensagens_usuario"]["boas_vindas"]
        mensagem_boas_vindas = mensagem_boas_vindas.replace("{usuario}", member.mention)
        print(f"[INFO] Canal encontrado: {channel.name}")
        await channel.send(mensagem_boas_vindas)
    else:
        print(f"[ERRO] Canal com ID {channel_id} não encontrado.")

# Evento disparado quando um membro é atualizado
@client.event
async def on_member_update(before: discord.Member, after: discord.Member):
    #Verifica se o usuário ganhou um novo cargo
    if len(before.roles) < len(after.roles):
        novo_cargo = next(role for role in after.roles if role not in before.roles)
        print(f"[EVENTO] Usuário {after.name} (ID: {after.id}) recebeu o cargo {novo_cargo.name}")
        
        channel_id = credentials["channel_welcome_id"]  #ID do canal de boas-vindas
        channel = after.guild.get_channel(channel_id)

        if channel:
            #================ deixar os cargos dinamicos tambem ================
            if novo_cargo.name == "ComboCompleto (CC)" or novo_cargo.name == "MeioCombo (MC)" or novo_cargo.name == "Netflix-Only":
                mensagem = texts["mensagens_usuario"]["registro_concluido"]
                mensagem = mensagem.replace("{usuario}", after.mention)
                mensagem = mensagem.replace("{nome_cargo}", novo_cargo.name)
                print(pagamentos.adicionar_usuario(username=after.name, cargo=novo_cargo.name))
                await channel.send(mensagem)
        
        else:
            print(f"[ERRO] Canal com ID {channel_id} não encontrado.")

# Evento disparado quando um membro é removido
@client.event
async def on_member_remove(member: discord.Member):
    print(f"[EVENTO] Usuário {member.name} (ID: {member.id}) saiu da guild {member.guild.name} (ID: {member.guild.id})")
    channel_id = credentials["channel_welcome_id"]  #ID do canal de boas-vindas
    channel = member.guild.get_channel(channel_id)
    if channel:
        mensagem_despedida = texts["mensagens_usuario"]["usuario_removido"]
        mensagem_despedida = mensagem_despedida.replace("{usuario}", member.mention)
        print(pagamentos.remover_usuario(username=member.name))
        await channel.send(mensagem_despedida)
    else:
        print(f"[ERRO] Canal com ID {channel_id} não encontrado.")
            
#======================================= COMANDOS // DEIXAR NOME E DESCRIÇÃO DINAMICOS ========================================
# Comando chatbot usando IA da gemini
@client.tree.command(name=comandos["chatbot"]["name"], description=comandos["chatbot"]["description"])
async def chatbot(interaction: discord.Interaction, mensagem: str):
    texto = f"o cargo do usuario é {interaction.user.top_role.name}\n{mensagem}"
    contexto = gerar_input_embeddings(texto)
    print(f"contexto gerado: {contexto}")
    await interaction.response.defer(ephemeral=True)
    
    resultado = await asyncio.to_thread(process_chatbot_message, mensagem, interaction.user.top_role.name, contexto)
    print(f"o usuario {interaction.user.name} fez a pergunta: {mensagem} e teve a resposta:\n{resultado}")
    await interaction.followup.send(resultado)

@client.tree.command(name=comandos["emailAI"]["name"], description=comandos["emailAI"]["description"])
async def codigo(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    resultado = process_unread_email_response()
    await interaction.followup.send(resultado)

@client.tree.command(name="valores", description="Lista de valores")
async def valores(interaction: discord.Interaction):
    file = discord.File("src/BotDiscord/images/valores.png", filename="valores.png")
    await interaction.response.send_message("Aqui estão os valores do combo: ", file=file)

@client.tree.command(name="cargo", description="meu cargo")
async def cargo(interaction: discord.Interaction):
    await interaction.response.send_message(f'Seu cargo é {interaction.user.top_role.name}')

@client.tree.command(name=comandos["anexoAI"]["name"], description=comandos["anexoAI"]["description"])
async def comprovante(interaction: discord.Interaction, anexo: discord.Attachment):
    await interaction.response.defer(ephemeral=True)
    save_path = f"src/BotDiscord/comprovantes/{anexo.filename}"
    print(f"Salvando o comprovante do usuario: {interaction.user.name} em {save_path}")
    await anexo.save(save_path)
    await interaction.followup.send(f"Comprovante recebido, verficando o pagamento...")
    resultado = process_pagamento(path=save_path, cargo=interaction.user.name)
    print(f"Resultado do pagamento: {resultado}")
    if resultado == "Pagamento confirmado com sucesso":
        mes_atual = meses_portugues[datetime.datetime.now().month - 1]
        print(pagamentos.adicionar_pagamento(username=interaction.user.name, mes=mes_atual))
    else:
        print("Pagamento não atualizado na base de dados")

    await interaction.followup.send(resultado, ephemeral=True)

    
@client.tree.command(name="comandos", description="Lista de comandos")
async def comandos(interaction: discord.Interaction):
    await interaction.response.send_message(
    "Comandos:\n"
    "/chatbot - Interaja com o nosso chatbot para obter respostas rápidas e tirar duvidas sobre o combo.\n"
    "/valores - Confira os valores das assinaturas.\n"
    "/comandos - Exibe esta lista de comandos disponíveis.\n"
    "/comprovante - Envie seu comprovante de pagamento."
    )


client.run(credentials["discord_token"])
