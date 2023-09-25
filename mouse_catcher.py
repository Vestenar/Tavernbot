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
delay_min = 20 * 60
delay_max = 60 * 60
ratio = 7
time_sleep = 10

with open('params.json', 'r') as file:
    bot_params = json.loads(file.read())
    chats = bot_params["mouse_hunt"]
    test_chats = bot_params["mouse_hunt_test"]

if settings.TEST_MODE:
    chats = test_chats
    delay_min = 5
    delay_max = 6
    ratio = 2
    time_sleep = 3


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
        scores_list = json.loads(file.read())["mice_caught"]
        if str(chat_id) not in scores_list:
            score_counter(chat_id, user_id, 0)
            return 0
        if str(user_id) in scores_list[str(chat_id)]:
            return scores_list[str(chat_id)][str(user_id)]
        else:
            return 0


def show_scores(chat_id):
    chatid = str(chat_id)
    mouse_name = chats[chatid]["names"][0]
    rats_name = chats[chatid]["names"][1]

    with open('mouse_scores.json') as file:
        scores = json.loads(file.read())["mice_caught"]
    with open('users.json') as file:
        user_list = json.loads(file.read())
    if str(chat_id) not in scores:
        return "В этом чате мышей не ловят"
    scores = scores[str(chat_id)]
    rating = f'<code>Рейтинг охотников на {mouse_name} в чате:\n'
    sorted_scores = sorted(scores, key=scores.get, reverse=True)
    total, total_rats = 0, 0
    total = sum([int(i) for i in scores.values() if int(i) > 0])
    total_rats = abs(sum([int(i) for i in scores.values() if int(i) < 0]))

    for id in sorted_scores:
        name = user_list[id]
        points = scores[id]
        if points == 0:
            continue
        if points % 100 == 0 or points % 111 == 0:
            points = 0
        if len(name) > 15:
            rating += name.split()[0] + '\n'
            name = ' '.join(name.split()[1:])
        if points > 0:
            rating += f'{name:<15} {points:>4} {points/total:>6.2%}\n'
        else:
            rating += f'{name:<15} {points:>4}\n'
    rating += f'{"—"*30}\nИТОГО: {total} {mouse_name}</code>'
    return rating


if __name__ == '__main__':

    while True:
        time.sleep(randint(delay_min, delay_max))
        msk_zone = pytz.timezone('Europe/Moscow')
        now = datetime.now(tz=msk_zone)
        if 7 <= now.hour < 23:
            for chat in chats.keys():
                rnd_mouse = choice(['mouse'] * ratio + ['rat'] * (10 - ratio))
                mouse_appear(bot, chat, rnd_mouse)
                time.sleep(time_sleep)

    # print(show_scores(-1001295840958))
    # score_counter(settings.MY_ID, settings.MY_ID, 2)
    # print(get_score(my_id, my_id))
    # save_user(123, 'name')