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
from get_credentials import get_discord_credentials

# Define os intents necessários
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

#Pegando as credenciais do discord
credentials = get_discord_credentials()

# Cria o cliente do Discord com CommandTree para os slash commands
class ClientBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
    
    async def setup_hook(self):
        # ID do servidor onde os comandos serão sincronizados
        guild = discord.Object(id=credentials["id_servidor"])
        # Copia os comandos globais para o guild específico
        self.tree.copy_global_to(guild=guild)
        # Sincroniza os comandos com o guild para que apareçam instantaneamente
        await self.tree.sync(guild=guild)
        print(f"Comandos sincronizados com a guild {guild.id}")

client = ClientBot()

# Tarefa agendada para enviar mensagem diariamente às 08:00
@tasks.loop(time=datetime.time(hour=18, minute=20, second=0, tzinfo=pytz.timezone('America/Sao_Paulo')))
async def mensagem_diaria():
    # ID do canal de agendamento
    channel = client.get_channel(credentials["channel_agendamento_id"])  # Ex: 123456789012345678
    if channel:
        print("Mensagem diária enviada com sucesso!")
        await channel.send("""@everyone 📢 **Já experimentou nossa IA?** 📢  

                            Com ela, você encontra **informações sobre filmes e séries** em segundos! 🎬✨  

                            🔍 **Quer saber mais sobre um título específico?** Digite **/chatbot** e descubra!  
                            🔑 **Esqueceu a senha de algum serviço?** Pergunte e receba ajuda na hora!  
                            📦 **Dúvidas sobre o combo?** Tire todas as suas questões por aqui!  

                            Simples, rápido e prático. Teste agora! 🚀💬"""
                        )

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
        print(f"[INFO] Canal encontrado: {channel.name}")
        await channel.send(f"Seja bem-vindo(a) ao servidor, Espere ate que seu registro seja concluido, {member.mention}! 🎉")
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
            if novo_cargo.name == "ComboCompleto (CC)" or novo_cargo.name == "MeioCombo (MC)" or novo_cargo.name == "Netflix-Only":
                await channel.send(f"Parabéns, {after.mention}! você foi registrado com sucesso, e seu acesso ao {novo_cargo.name}! foi liberado 🎉\nAcesse o canal principal e digite /comandos")
        
        else:
            print(f"[ERRO] Canal com ID {channel_id} não encontrado.")
            

# Comando chatbot usando IA da gemini
@client.tree.command(name="chatbot", description="Chatbot sobre dúvidas")
async def chatbot(interaction: discord.Interaction, mensagem: str):
    texto = f"o cargo do usuario é {interaction.user.top_role.name}\n{mensagem}"
    contexto = gerar_input_embeddings(texto)
    print(f"contexto gerado: {contexto}")
    await interaction.response.defer(ephemeral=True)
    
    resultado = await asyncio.to_thread(process_chatbot_message, mensagem, interaction.user.top_role.name, contexto)
    print(f"o usuario {interaction.user.name} fez a pergunta: {mensagem} e teve a resposta:\n{resultado}")
    await interaction.followup.send(resultado)

@client.tree.command(name="codigo", description="Busca o código de acesso no email")
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

@client.tree.command(name="comprovante", description="Envie o comprovante de pagamento")
async def comprovante(interaction: discord.Interaction, anexo: discord.Attachment):
    await interaction.response.defer(ephemeral=True)
    save_path = f"src/BotDiscord/comprovantes/{anexo.filename}"
    await anexo.save(save_path)
    await interaction.followup.send(f"Comprovante recebido, verficando o pagamento...")
    resultado = process_pagamento(path=save_path, cargo=interaction.user.top_role.name)
    await interaction.followup.send(resultado)

    
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
