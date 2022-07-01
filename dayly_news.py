import requests
import getgodville
from settings import CHATS, BOT_TOKEN

prognoz = 'Всем доброе утро! Утренняя сводка новостей от бармена:\n' + getgodville.god_prognoz() + '\n'
coupon = getgodville.get_coupon()
for chat_id in CHATS:
    leaving = getgodville.god_guild(CHATS[chat_id])

    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={chat_id}&text={prognoz + leaving + coupon}'
    resp = requests.get(url)
    # print(prognoz + leaving + coupon)
