import requests
import getgodville
from settings import CHATS, BOT_TOKEN, ZST_ID
from jump_counter import autostart_timers
from telebot import TeleBot
from datetime import datetime


now_str = datetime.now().strftime('%d.%m.%Y года')
prognoz = f'Всем доброе утро! Сегодня {now_str}\nУтренняя сводка новостей от бармена:\n{getgodville.god_prognoz()}\n\n'
coupon = getgodville.get_coupon()
for chat_id in CHATS:
    leaving = getgodville.god_guild(CHATS[chat_id])

    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={chat_id}&text={prognoz + leaving + coupon}'
    resp = requests.get(url)
    # print(f'{now_str}: {CHATS[chat_id]} status {resp.status_code}')
    # print(prognoz + leaving + coupon)

# ------<<<------ Перезапуск таймеров ------>>>------
chatlist = [ZST_ID]
user_timers = []
bot_token = BOT_TOKEN
bot = TeleBot(bot_token)
for chat in chatlist:
    autostart_timers(bot, chat, user_timers)
