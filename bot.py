import json
import logging
import random
import sys
import time
from pprint import pprint

import pytz
from telebot import TeleBot, apihelper
from datetime import datetime, timedelta
from random import choice
import getinfo
import replies
import menu_games
import timetojump
import jump_counter
import settings
import mouse_catcher

# ------<<<------ Инициализация ------>>>------
bot_token = settings.BOT_TOKEN
my_id = settings.MY_ID
warning_to = settings.WHOWARN

# ------<<<------ Инициализация мини-игр ------>>>------
xo_state = [' '] * 9
xo_message_to_delete, xo_turn = (None, None)
mouse_busy = time.time()
last_call = [0.0]

raschlenenka_cost = 20
raschlenenka_off_cost = 2
shower_cost = 10

bot = TeleBot(bot_token)

# ------<<<------ Оповещения о перезапуске ------>>>------
for ident in warning_to.keys():
    if not settings.TEST_MODE:
        try:
            bot.send_message(ident, 'Я перезапущен, таймеры сброшены')
        except apihelper.ApiTelegramException:
            bot.send_message(my_id, f'{ident} заблокировал личные сообщения бота')


# ------<<<------ Логирование сообщений ------>>>------     # TODO переделать с использованием logging(info)
def logging_messages(message):
    if message.chat.type == 'private' and message.from_user.id != my_id:
        with open(r'tavernmessages.log', 'a') as logfile:
            logfile.write('{}\t{} {}:\t{}\n'.format(datetime.now(), message.from_user.id,
                                                    message.from_user.first_name, message.text))


@bot.message_handler(commands=['start'])
def start_message(message):
    logging_messages(message)
    bot.send_message(message.chat.id, 'Бармен приветствует Вас в Старой Таверне! '
                                      'Для получения информации отправьте команду /skills')


@bot.message_handler(commands=['help'])
def help_message(message):
    logging_messages(message)
    bot.send_message(message.chat.id,
                     'Бот может выбрать случайное время для вечернего похода гильдии в 22 часа в интервале '
                     'от 00 до 15 минут.\nВ 12 часов и в 17 часов время зафиксировано.'
                     '\nБолее подробную информацию можно получить по команде /skills')


@bot.message_handler(commands=['curs'])
def curs_message(message):
    logging_messages(message)
    bot.send_message(message.chat.id, getinfo.get_currencies())


@bot.message_handler(commands=['skills'])
def skills_menu(message):
    logging_messages(message)
    menu_games.skills_menu(bot, message)


# ------<<<------ Прислать файл со списком гильдии ------>>>------
@bot.message_handler(commands=['guildlist'])
def list_message(message):
    logging_messages(message)
    from getgodville import list_god_guild
    guildname = message.text[10:].strip()
    filename = list_god_guild(guildname) if guildname else list_god_guild()
    if not filename:
        bot.send_message(message.chat.id, 'Название гильдии введено неправильно')
    else:
        bot.send_document(message.chat.id, open(filename, 'rb'))


# ------<<<------ Отобразить менюшку таймеров ------>>>------
@bot.message_handler(regexp=r'(дай|поставь|назначь|установи).* (время|таймер|напомин)|'
                            r'(назначь|напомни).* (данж|море|полигон|поход)')
def dungeon(message):
    logging_messages(message)
    menu_games.jump_menu(bot, message)


# ------<<<------ Отобразить менюшку напоминаний ------>>>------
@bot.message_handler(commands=['reminder'])
def del_reminder(message):
    logging_messages(message)
    if message.chat.type in ['group', 'supergroup']:
        menu_games.reminder_menu(bot, message)
    else:
        bot.send_message(message.chat.id, 'Установка персонального напоминания возможна только в групповом чате')


# ------<<<------ Отобразить рейтинг мышиной охоты ------>>>------
@bot.message_handler(commands=['scores'])
def show_scores(message):
    table = mouse_catcher.show_scores(message.chat.id)
    bot.send_message(message.chat.id, table, parse_mode='html')


@bot.message_handler(commands=['shop'])
def show_shop(message):
    menu_games.shop_menu(bot, message)


# ------<<<------ Отобразить менюшку игр ------>>>------
@bot.message_handler(regexp=r'(поиграем|сыграем|играть)')
def dungeon(message):
    logging_messages(message)
    menu_games.games_menu(bot, message)


# ------<<<------ Отобразить менюшку вызова ------>>>------
@bot.message_handler(regexp=r'(!зови|ал(а|я)рм)|!!!')
def alert(message):
    logging_messages(message)
    menu_games.alert_menu(bot, message)


# ------<<<------ Отработка команд из всех менюшек ------>>>------
@bot.callback_query_handler(func=lambda call: True)
def callback_buttons(call):
    global xo_message_to_delete, xo_turn, xo_state
    global mouse_busy
    global last_call

    if call.message:

        user = call.from_user
        first_name = user.first_name if user.first_name else ''
        last_name = (' ' + user.last_name) if user.last_name else ''
        username = first_name + last_name
        chats, raschlenenka, raschlenenka_till, liven = mouse_catcher.get_hunt_params()

        if call.data.startswith('прыг'):
            _, event, *event_time = call.data.split(',')
            a = jump_counter.CounterJump(bot, call, event_name=event, event_time=event_time)
            a.run()

        elif call.data in ['10sec', '60sec']:
            ss = int(call.data[:2])
            a = jump_counter.CounterJump(bot, call)
            a.run_fast(ss)

        elif call.data == 'settime':
            a = jump_counter.CounterJump(bot, call)
            a.run()

        elif call.data in ['reminder1', 'reminder2', 'reminder3', 'reminder5']:
            warn_time = call.data[-1]
            updater = jump_counter.WarnUpdater(bot, call, warn_time)
            updater.set_reminder()

        elif call.data == 'reminderoff':
            updater = jump_counter.WarnUpdater(bot, call)
            updater.remove_reminder()

        # ------<<<------ Описание из /skills ------>>>------
        elif call.data == 'story':
            bot.send_message(call.message.chat.id, 'Попросите бармена рассказать/поведать '
                                                   'историю/байку/анекдот или просто повеселить')
        elif call.data == 'curse':
            bot.send_message(call.message.chat.id, 'Узнайте у бармена про ситуации на биржах/о курсах валют/'
                                                   'что почем/куда вкладывать')
        elif call.data == 'GV_player':
            bot.send_message(call.message.chat.id, 'Попросите рассказать/шепнуть/узнать какие слухи '
                                                   'или спросить, что знает/слышал бот о любом игроке из Годвилля')
        elif call.data == 'timer':
            bot.send_message(call.message.chat.id, 'Можно попросить установить таймер/время/напоминание '
                                                   'или напомнить про данж/море/полигон/поход. ')
        elif call.data == 'movie':
            bot.send_message(call.message.chat.id, 'Спросите что посмотреть, и бармен попробует '
                                                   'посоветовать фильм')
        elif call.data == 'recipe':
            bot.send_message(call.message.chat.id, 'Можно спросить бармена научить готовить коктейль/ '
                                                   'дать рецепт напитка')

        elif call.data == 'games':
            bot.send_message(call.message.chat.id, 'Сыграйте с барменом в короткий квест на выживание или '
                                                   'в крестики-нолики (команда сыграем/поиграем)')

        elif call.data == 'football':
            bot.send_message(call.message.chat.id, 'Спросите у бота про главные футбольные события года '
                                                   '(лиги Европы, чемпионов, конференций и чемпионат мира) чтобы '
                                                   'получить таблицу актуального этапа. '
                                                   'Если в запросе указать интересующую группу (A, B, C, ...), '
                                                   'то будет показана только таблица группы.')
        elif call.data == 'reminder':
            bot.send_message(call.message.chat.id, 'Установите персональное напоминание в личку '
                                                   'о предстоящем походе. Работает только для группы, '
                                                   'в которой вызывается команда /reminder')

        elif call.data == 'menu_bar':
            from menu_games import bar_menu
            bar_menu(bot, call)

        elif call.data == 'closemenu':
            bot.delete_message(call.message.chat.id, call.message.message_id)
            xo_state = [' '] * 9

        elif call.data in ['пиво', 'вино', 'ламбруско', 'сидр', 'налей']:
            rep_message, rep_type = replies.reply(call.data)
            if rep_type == 'text':
                bot.send_message(call.message.chat.id, rep_message)
            elif rep_type == 'sticker':
                bot.send_sticker(call.message.chat.id, rep_message)

        elif call.data == 'wherewater':
            from menu_games import where_is_water
            name = call.from_user.first_name
            bot.delete_message(call.message.chat.id, call.message.message_id)
            where_is_water(bot, call.message.chat.id, name)

        elif call.data == 'cave':
            from menu_games import where_is_water_1
            wherewater_way = choice(['safe', 'not safe'])
            bot.delete_message(call.message.chat.id, call.message.message_id)
            if wherewater_way == 'safe':
                where_is_water_1(bot, call.message, call.from_user, True)
            elif wherewater_way == 'not safe':
                where_is_water_1(bot, call.message, call.from_user, False)

        elif call.data == 'rassol':
            from time import sleep
            wherewater_way = choice(['win', 'lose'])
            sleep(2)
            bot.delete_message(call.message.chat.id, call.message.message_id)
            if wherewater_way == 'win':
                bot.send_message(call.message.chat.id, f'Итак, бочонок рассола был успешно раздобыт и доставлен в '
                                                       f'Таверну! Слава спасителю {call.from_user.first_name}! '
                                                       f'Налейте Герою!!!')
            elif wherewater_way == 'lose':
                bot.send_message(call.message.chat.id, 'Итак, бочонок был успешно раздобыт и доставлен в Таверну! '
                                                       'Увы, вместо рассола в нем оказался обычный березовый сок с '
                                                       'мякотью, что совершенно не помогает в борьбе с коварным '
                                                       'Бодуном! Найдется ли другой смельчак?')

        elif call.data == 'X-O':
            xo_state = [' '] * 9
            xo_turn = choice(['Barmen', 'Player'])
            if xo_turn == 'Barmen':
                xo_state[4] = 'O'
            xo_message_to_delete = menu_games.cross_zeros(bot, call, call.message.id, xo_state)
        elif call.data.startswith('xo'):
            n = int(call.data[-1])
            if xo_state[n] == ' ':
                xo_state[n] = 'X'
                xo_state = menu_games.xo_end_game(xo_state)
                xo_state = menu_games.xo_bot_move(xo_state)
                xo_state = menu_games.xo_end_game(xo_state)
                xo_message_to_delete = menu_games.cross_zeros(bot, call, xo_message_to_delete, xo_state)

        elif call.data == 'mouse_caught':
            pressed = time.time()
            chat_id = str(call.message.chat.id)
            mouse_name = chats[chat_id]["names"][0]
            rat_name = chats[chat_id]["names"][1]
            if time.time() > raschlenenka_till and raschlenenka:
                raschlenenka = False
                mouse_catcher.set_raschlenenka(False)
                for chat in chats.keys():
                    chat_mouse_name = chats[chat]["names"][0]
                    bot.send_message(chat, f'Ну вот и все. Оплаченное время веселья закончилось, '
                                           f'больше {chat_mouse_name} рвать нельзя. Продлевать будете?')

            if (time.time() - mouse_busy) > 5:
                if not raschlenenka:
                    mouse_busy = time.time()
                try:
                    bot.delete_message(call.message.chat.id, call.message.id)
                except:
                    pass
                reaction = round(pressed - call.message.date, 3)
                if reaction < 100:
                    score = mouse_catcher.score_counter(call.message.chat.id, call.from_user.id, 1, reaction)
                else:
                    score = mouse_catcher.score_counter(call.message.chat.id, call.from_user.id, 1)
                    reaction = '+0.1'
                if score % 111 == 0 or score % 100 == 0:
                    bot.send_message(call.message.chat.id, f'УУУПС! Случившийся катаклизм избавил {username} от '
                                                           f'популяции {mouse_name} полностью. Теперь на счету 0.')
                else:
                    if score >= 0:
                        bot.send_message(call.message.chat.id, f'Фух, поймали за {reaction} сек! '
                                                               f'На счету {username}: {score} {mouse_name}.')
                    else:
                        bot.send_message(call.message.chat.id, f'Фух, поймали за {reaction} сек! Одна {rat_name}'
                                                               f' лопнула и теперь На счету {username}: {abs(score)} .')

                mouse_catcher.save_user(call.from_user.id, username)
                if not raschlenenka:
                    mouse_busy = time.time()

        elif call.data == 'rat_caught':
            chat_id = str(call.message.chat.id)
            mouse_name = chats[chat_id]["names"][0]
            rat_name = chats[chat_id]["names"][1]

            if (time.time() - mouse_busy) > 5:
                mouse_busy = time.time()
                try:
                    bot.delete_message(call.message.chat.id, call.message.id)
                except:
                    pass

                user_scores = mouse_catcher.get_score(call.message.chat.id, call.from_user.id)
                if user_scores > 0:
                    mouse_eaten = random.randint(min(3, user_scores), min(10, user_scores))
                else:
                    mouse_eaten = 1
                score = mouse_catcher.score_counter(call.message.chat.id, call.from_user.id, - mouse_eaten)
                if user_scores <= 0:
                    bot.send_message(call.message.chat.id, f'Ух ты! Пойманная {rat_name} не нашла {mouse_name}, '
                                                           f'поэтому поселилась у {username}, '
                                                           f'и теперь их {abs(user_scores) + 1}.')
                else:
                    bot.send_message(call.message.chat.id, f'Упс! Пойманная {rat_name} пожрала {mouse_name} '
                                                           f'у {username}, аж {mouse_eaten} за раз! '
                                                           f'Теперь на счету {score}.')
                mouse_catcher.save_user(call.from_user.id, username)
                mouse_busy = time.time()

        if call.data.startswith('расчлененка'):
            chat_id = str(call.message.chat.id)
            user_scores = mouse_catcher.get_score(chat_id, call.from_user.id)
            if call.data.endswith('вкл'):
                if raschlenenka:
                    return
                if user_scores >= raschlenenka_cost:
                    mouse_catcher.score_counter(call.message.chat.id, call.from_user.id, - raschlenenka_cost)
                    raschlenenka = True

                    for chat in chats.keys():
                        chat_mouse_name = chats[chat]["names"][0]
                        bot.send_message(chat, f'Внимание! В одном из чатов состоялась сделка с {username}! '
                                               f'Теперь {chat_mouse_name} временно можно рвать на части!')
                else:
                    bot.send_message(call.message.chat.id, f'Это не банк, {username}, тут в долг не дают!')

            elif call.data.endswith('откл'):
                raschlenenka = False
                if user_scores >= raschlenenka_off_cost:
                    mouse_catcher.score_counter(call.message.chat.id, call.from_user.id, - raschlenenka_off_cost)
                    for chat in chats.keys():
                        chat_mouse_name = chats[chat]["names"][0]
                        bot.send_message(chat, f'Внимание! В одном из чатов состоялась сделка с {username}! '
                                               f'Теперь {chat_mouse_name} снова рвать нельзя!')
                else:
                    bot.send_message(call.message.chat.id, f'Это не банк, {username}, тут в долг не дают!')
            mouse_catcher.set_raschlenenka(raschlenenka)

        if call.data == 'мышепад':
            msk_zone = pytz.timezone('Europe/Moscow')
            now = datetime.now(tz=msk_zone)

            if 7 <= now.hour < 23:
                if liven:
                    return
                chat_id = str(call.message.chat.id)
                user_scores = mouse_catcher.get_score(chat_id, call.from_user.id)
                if user_scores >= shower_cost:
                    mouse_catcher.score_counter(call.message.chat.id, call.from_user.id, - shower_cost)
                    mouse_catcher.set_shower(True)

                    for chat in chats.keys():
                        chat_mouse_name = chats[chat]["names"][0]
                        bot.send_message(chat, f'Внимание! В одном из чатов состоялась сделка с {username}! '
                                               f'В некоторых чатах включен дождик, ловите больше {chat_mouse_name}!')

                    mouse_catcher.start_mouse_shower(bot, username, chats)

                else:
                    bot.send_message(call.message.chat.id, f'Это не банк, {username}, тут в долг не дают!')


            else:
                bot.send_message(call.message.chat.id, f'У нас ночь, {username} все спят, даже тучки!')

        if call.data.startswith('alert'):
            now = time.time()
            last_call = list(filter(lambda x: x + 10 > now, last_call))
            last_call.append(now)
            user = call.from_user
            first_name = user.first_name if user.first_name else ''
            last_name = (' ' + user.last_name) if user.last_name else ''
            username = first_name + last_name

            if 'vest' in call.data:
                brevno_name = 'vestenar'
                brevno_id = settings.MY_ID

            elif 'rose' in call.data:
                brevno_name = 'i_potterman'
                brevno_id = None

            elif 'temn' in call.data:
                brevno_name = 'kosa_kosya'
                brevno_id = None

            if len(last_call) < 6:
                rest = 5 - len(last_call)
                bot.send_message(call.message.chat.id, f'@{brevno_name}, тебя зовет {username}. <i>ост.{rest}</i>',
                                 parse_mode='html')
                if brevno_id is not None:
                    bot.send_message(brevno_id, f'@{brevno_name}, тебя зовет {username}')


@bot.message_handler(regexp=r'!log')
def send_logs(message):
    if message.json['from']['id'] == my_id:
        bot.send_document(message.chat.id, open(r'tavernerrors.log', 'rb'))
        bot.send_document(message.chat.id, open(r'tavernmessages.log', 'rb'))
        bot.send_document(message.chat.id, open(r'unpinerrors.log', 'rb'))
        bot.send_document(message.chat.id, open(r'params.json', 'rb'))
        bot.send_document(message.chat.id, open(r'timers.txt', 'rb'))


@bot.message_handler(regexp=r'!deletelog')
def delete_logs(message):
    if message.json['from']['id'] == my_id:
        with open(r'tavernerrors.log', 'w') as file:
            file.write('cleared by request at {}\n'.format(datetime.now()))
        with open(r'unpinerrors.log', 'w') as file:
            file.write('cleared by request at {}\n'.format(datetime.now()))


@bot.message_handler(regexp=r'!reload')
def reload_modules(message):
    if message.json['from']['id'] == my_id:
        import importlib
        importlib.reload(getinfo)
        importlib.reload(replies)
        importlib.reload(menu_games)
        importlib.reload(timetojump)
        importlib.reload(jump_counter)
        importlib.reload(mouse_catcher)
        bot.send_message(message.chat.id, 'Модули перегружены')


@bot.message_handler(regexp=r'!chatid')
def reload_modules(message):
    if message.json['from']['id'] == my_id:
        bot.send_message(message.chat.id, f'chat ID is: {message.chat.id}')


@bot.message_handler(content_types=['text'])
def reply_text(message):
    logging_messages(message)

    rep_message, rep_type = replies.reply(message)
    if rep_type == 'text':
        bot.send_message(message.chat.id, rep_message, parse_mode='html')
    elif rep_type == 'sticker':
        bot.send_sticker(message.chat.id, rep_message)
    elif rep_type == 'img':
        pic_text, text, img = rep_message
        if img and img not in ['https://www.povarenok.ru/images/recipes/1.gif',
                               'https://www.povarenok.ru/data/cache/2014sep/16/34/863313_88985-330x220x.jpg']:
            bot.send_photo(message.chat.id, img, pic_text)
            if text:
                bot.send_message(message.chat.id, text)
        else:
            bot.send_message(message.chat.id, (pic_text, text))
            bot.send_message(message.chat.id, text)


# @bot.message_handler(content_types=['sticker'])
# def get_sticker(message):
#     from pprint import pprint
#     pprint(message.json)


logging.basicConfig(filename="tavernerrors.log", format='%(asctime)s - %(message)s', level=logging.ERROR)
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as error:
        logging.error(error)
        bot.stop_polling()
        time.sleep(15)
