from datetime import datetime
import pytz
from telebot import TeleBot
import settings
import time
from random import randint, choice
from menu_games import mouse_appear
import json

bot_token = settings.BOT_TOKEN
bot = TeleBot(bot_token)
my_id = settings.MY_ID
chats = settings.CHATS
# chats = [settings.MY_ID]
now = pytz.timezone('UTC')
delay_min = 20 * 60
delay_max = 60 * 60
ratio = 7


def score_counter(chat_id, user_id, score):
    chat_id, user_id = str(chat_id), str(user_id)
    with open('mouse_scores.json') as file:
        scores = json.loads(file.read())
        current_chat = scores["mice_caught"].setdefault(chat_id, {})
        current_user_scores = current_chat.setdefault(user_id, 0)
        scores["mice_caught"][chat_id][user_id] += score
    with open('mouse_scores.json', 'w') as file:
        file.write(json.dumps(scores))
    return current_user_scores + score


def save_user(user_id, username):
    with open('users.json', 'r') as file:
        user_list = json.loads(file.read())
        if str(user_id) not in user_list:
            user_list[str(user_id)] = username
            with open('users.json', 'w') as file:
                file.write(json.dumps(user_list))


def get_score(chat_id, user_id):
    with open('mouse_scores.json') as file:
        scores = json.loads(file.read())["mice_caught"][str(chat_id)]
    return scores[str(user_id)]


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
                rnd_mouse = choice(['mouse'] * ratio + ['rat'] * (10 - ratio))
                mouse_appear(bot, chat, rnd_mouse)
                time.sleep(30)

    # print(show_scores(-1001320841683))
    # score_counter(settings.MY_ID, settings.MY_ID, 2)