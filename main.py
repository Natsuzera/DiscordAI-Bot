import datetime
import pytz

tz = pytz.timezone('America/Sao_Paulo')
now = datetime.datetime.now(tz)

print(now.month)