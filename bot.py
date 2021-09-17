import logging
from telebot import TeleBot
from datetime import datetime
from random import choice
import getinfo
import replies
import menu_games
import timetojump
import settings

# ------<<<------ Инициализация ------>>>------
bot_token = settings.BOT_TOKEN
my_id = settings.MY_ID
warning_to = settings.WHOWARN

# ------<<<------ Инициализация X-O ------>>>------
xo_state = [' '] * 9
xo_message_to_delete, xo_turn = (None, None)

bot = TeleBot(bot_token)
# telebot.apihelper.proxy = {'https': 'socks5h://alexneupok_9cmkn:gpbvksqrce@socks-us.windscribe.com:1080'}

# ------<<<------ Оповещения о перезапуске ------>>>------
for ident in warning_to.keys():
    bot.send_message(ident, 'Я перезапущен, таймеры сброшены')


# ------<<<------ Логирование сообщений ------>>>------     # TODO переделать с использованием logging(info)
def logging_messages(message):
    if message.chat.type == 'private' and message.from_user.id != my_id:
        with open(r'tavernmessages.log', 'a') as logfile:
            logfile.write('{}\t{} {}:\t{}\n'.format(datetime.now(), message.from_user.id,
                                                    message.from_user.first_name, message.text))


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Бармен приветствует Вас в Старой Таверне! '
                                      'Для получения информации отправьте команду /skills')


@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(message.chat.id,
                     'Бот может выбрать случайное время для вечернего похода гильдии в 22 часа в интервале '
                     'от 00 до 15 минут.\nВ 12 часов и в 17 часов время зафиксировано.'
                     '\nБолее подробную информацию можно получить по команде /skills')


@bot.message_handler(commands=['curs'])
def curs_message(message):
    bot.send_message(message.chat.id, getinfo.get_currencies())


@bot.message_handler(commands=['skills'])
def skills_menu(message):
    menu_games.skills_menu(bot, message)


# ------<<<------ Отобразить менюшку таймеров ------>>>------
@bot.message_handler(regexp=r'(дай|назначь|установи) (время|таймер|напомин)|'
                            r'(назначь|напомни).* (данж|море|полигон|поход)')
def dungeon(message):
    logging_messages(message)
    menu_games.jump_menu(bot, message)


# ------<<<------ Отобразить менюшку игр ------>>>------
@bot.message_handler(regexp=r'(поиграем|сыграем|играть)')
def dungeon(message):
    logging_messages(message)
    menu_games.games_menu(bot, message)


# ------<<<------ Отработка команд из всех менюшек ------>>>------
@bot.callback_query_handler(func=lambda call: True)
def callback_buttons(call):
    global xo_message_to_delete, xo_turn, xo_state
    if call.message:

        if call.data in ['прыг 12', 'прыг 17', 'прыг 22']:
            hh = int(call.data.split()[1])
            timetojump.start_dungeon(bot, call, regular=True, time_msg=hh)

        elif call.data == 'settime':
            timetojump.start_dungeon(bot, call, regular=False)

        elif call.data == 'story':
            bot.send_message(call.message.chat.id, 'Попросите бармена рассказать/поведать '
                                                   'историю/байку/анекдот или просто повеселить')
        elif call.data == 'curse':
            bot.send_message(call.message.chat.id, 'Узнайте у бармена про ситуации на биржах/о курсах валют/'
                                                   'что почем/куда вкладывать')
        elif call.data == 'GV_player':
            bot.send_message(call.message.chat.id, 'Можно попросить рассказать/шепнуть/узнать какие слухи '
                                                   'или спросить, что знает/слышал бот, о любом игроке из Годвилля')
        elif call.data == 'timer':
            bot.send_message(call.message.chat.id, 'Можно попросить установить таймер/время/напоминание '
                                                   'или поросить бармена напомнить про данж/море/полигон/поход')
        elif call.data == 'movie':
            bot.send_message(call.message.chat.id, 'Можно спросить, что посмотреть, и бармен попробует '
                                                   'посоветовать фильм')
        elif call.data == 'recipe':
            bot.send_message(call.message.chat.id, 'Можно спросить бармена научить готовить коктейль/ '
                                                   'дать рецепт напитка')

        elif call.data == 'games':
            bot.send_message(call.message.chat.id, 'Можно сыграть с барменом в короткий квест на выживание или '
                                                   'в крестики-нолики (сыграем/поиграем)')

        elif call.data == 'football':
            bot.send_message(call.message.chat.id, 'Спросите у бота про главные футбольные события года '
                                                   '(лиги Европы, чемпионов, конференций и чемпионат мира) чтобы '
                                                   'получить таблицу актуального этапа.'
                                                   'Если в запросе указать интересующую группу (A, B, C, ...), '
                                                   'то будет показана только таблица группы')

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


@bot.message_handler(regexp=r'!log')
def send_logs(message):
    if message.json['from']['id'] == my_id:
        bot.send_document(message.chat.id, open(r'tavernerrors.log', 'rb'))
        bot.send_document(message.chat.id, open(r'tavernmessages.log', 'rb'))
        bot.send_document(message.chat.id, open(r'unpinerrors.log', 'rb'))


@bot.message_handler(regexp=r'!deletelog')
def delete_logs(message):
    if message.json['from']['id'] == my_id:
        with open(r'tavernerrors.log', 'w') as file:
            file.write('cleared by request at {}\n'.format(datetime.now()))
        with open(r'tavernmessages.log', 'w') as file:
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
        bot.send_message(message.chat.id, 'Модули перегружены')


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
#     chat_id = (-1001320841683)
#     print(message.json)

logging.basicConfig(filename="tavernerrors.log", format='%(asctime)s - %(message)s', level=logging.ERROR)
try:
    bot.polling(none_stop=True)
except Exception:
    pass
