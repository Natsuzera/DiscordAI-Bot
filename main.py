import datetime
mes_atual = datetime.datetime.now().month
meses_portugues = [
    "janeiro", "fevereiro", "março", "abril", "maio", "junho",
    "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"
]
mes_atual = meses_portugues[mes_atual - 1]
print(mes_atual)