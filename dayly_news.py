import requests
import getgodville
import json
import getinfo

with open('params.txt') as init_file:
    bot_params = json.loads(init_file.read())
    bot_token = bot_params["bot_token"]

chats = {'-1001169842809': 'asylum mortuis', '-1001320841683': 'Завсегдатаи Старой Таверны'}

prognoz = 'Всем доброе утро! Утренняя сводка новостей от бармена:\n' + getgodville.god_prognoz() + '\n'
for chat_id in chats:
    leaving = getgodville.god_guild(chats[chat_id])
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={prognoz + leaving}'
    resp = requests.get(url)

chat_id = '297112989'
text = getinfo.get_promo()

if text:
    text = 'Свежие коды для genshin: \n' + text
else:
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={text}'
    requests.get(url)
