from datetime import datetime
import pytz
from telebot import TeleBot
import settings
import time
from random import randint
from menu_games import mouse_appear
import json

bot_token = settings.BOT_TOKEN
bot = TeleBot(bot_token)
my_id = settings.MY_ID
chats = settings.CHATS
now = pytz.timezone('UTC')
delay_min = 20 * 60
delay_max = 60 * 60


def score_counter(chat_id, user_id):
    chat_id, user_id = str(chat_id), str(user_id)
    with open('mouse_scores.json', 'r+') as file:
        scores = json.loads(file.read())
        file.seek(0)
        current_chat = scores["mice_caught"].setdefault(chat_id, {})
        current_user_scores = current_chat.setdefault(user_id, 0)
        scores["mice_caught"][chat_id][user_id] += 1
        file.write(json.dumps(scores))
    return current_user_scores + 1


def save_user(user_id, username):
    with open('users.json', 'r') as file:
        user_list = json.loads(file.read())
        file.seek(0)
        if str(user_id) not in user_list:
            user_list[str(user_id)] = username
            with open('users.json', 'w') as file:
                file.write(json.dumps(user_list))


def show_scores(chat_id):
    with open('mouse_scores.json') as file:
        scores = json.loads(file.read())["mice_caught"]
    with open('users.json') as file:
        user_list = json.loads(file.read())
    if str(chat_id) not in scores:
        return "В этом чате мышей не ловят"
    scores = scores[str(chat_id)]
    rating = 'Рейтинг охотников на мышек в чате:\n'
    sorted_scores = sorted(scores, key=scores.get, reverse=True)
    for id in sorted_scores:
        name = user_list[id]
        rating += f'{name}: {scores[id]}\n'
    return rating


if __name__ == '__main__':
    while True:
        time.sleep(randint(delay_min, delay_max))
        utc_time = now.localize(datetime.utcnow())
        if 7 <= ((utc_time.hour + 27) % 24) < 23:
            for chat in chats:
                mouse_appear(bot, chat)
                time.sleep(30)

    # print(show_scores(-1001320841683))