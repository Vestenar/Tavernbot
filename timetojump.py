import json
from datetime import datetime
from random import randint, choice
import time
from telebot import types, apihelper
from threading import Thread
import pytz


def checktime22():
    with open('params.txt') as file:
        bot_params = json.loads(file.read())
        read_time = bot_params['timer22']
    now = time.localtime()
    if read_time['date'] == now.tm_mday:
        mm = read_time['mm']
        ss = read_time['ss']
        timewasset = True
    else:
        mm = randint(0, 15)
        ss = randint(0, 59)
        timewasset = False
        bot_params['timer22'] = {'date': now.tm_mday, 'mm': mm, 'ss': ss}

        with open('params.txt', 'w') as file:
            file.write(json.dumps(bot_params))

    return mm, ss, timewasset


def warn(bot, message, hours, minutes=00, seconds=00, rnd=False):
    invitetodungeon = ["Поход назначен на", "А пожалуйста!", "А пойдемте в данж! В", "Не перепутайте кнопки. Сбор в"]

    mins, secs, timeset = (minutes, seconds, False)
    if not rnd:
        if hours == 12:
            mins, secs = (1, 12)
        elif hours == 17:
            mins, secs = (1, 17)
        elif hours == 22:
            mins, secs, timeset = checktime22()
    else:
        hours, mins, secs = hours, minutes, seconds

    utc = pytz.timezone('UTC')
    now = utc.localize(datetime.utcnow())
    target_time = datetime(now.year, now.month, now.day, ((hours + 21) % 24), mins, secs, tzinfo=utc)
    time_delta = target_time - now
    delta = time_delta.seconds

    def countdown():
        todel = []
        for i in range(3):
            n = bot.send_message(message.chat.id, 3 - i)
            todel.append(n)
            time.sleep(1)
        bot.send_message(message.chat.id, 'Вперёд! Удачно вам сходить!')
        for i in todel:
            time.sleep(1)
            bot.delete_message(message.chat.id, i.message_id)

    if time_delta.days >= 0:
        if not rnd:
            if timeset:
                bot.send_message(message.chat.id, 'Сегодняшнее время уже было назначено на '
                                                  '{}:{:02d}:{:02d}.'.format(hours, mins, secs))
            else:
                bot.send_message(message.chat.id, '{} {}:{:02d}:{:02d}.'.format(choice(invitetodungeon),
                                                                                hours, mins, secs))
        if delta > 120:
            time.sleep(delta - 120)
            bot.send_message(message.chat.id, 'Приготовьтесь, осталось 2 минуты')
            delta = 120
        if delta > 30:
            time.sleep(delta - 30)
            ready30 = bot.send_message(message.chat.id, 'Приготовьтесь, осталось 30 секунд')
            message_pinned = False
            if message.json['chat']['type'] in ['group', 'supergroup']:
                try:
                    bot.pin_chat_message(message.chat.id, ready30.message_id)
                    message_pinned = True
                except apihelper.ApiTelegramException:
                    import sys
                    with open(r'unpinerrors.log', 'a') as logfile:
                        logfile.write(format(sys.exc_info()[0]))
            now = utc.localize(datetime.utcnow())  # time correction
            delta = (target_time - now).seconds
            time.sleep(delta - 3)
            countdown()
            if message_pinned:
                try:
                    bot.unpin_chat_message(message.chat.id, ready30.message_id)
                    bot.unpin_all_chat_messages(message.chat.id)            # FIXME сломалось по неясной причине
                except apihelper.ApiTelegramException:
                    import sys
                    with open(r'unpinerrors.log', 'a') as logfile:
                        logfile.write(format(sys.exc_info()[0]))
        else:
            bot.send_message(message.chat.id, 'Приготовьтесь, осталось {} секунд'.format(delta))
            time.sleep(delta - 3)
            countdown()
    else:
        bot.send_message(message.chat.id, 'Предлагаю завтрашний поход cпланировать завтра!')
    return


def start_dungeon(bot, call, regular, time_msg=None):
    def set_warn(message):
        hh, mm, ss = (0, 0, 0)
        try:
            message_time = message.text.split() + ['']
            data, dngn_type = list(map(int, message_time[0].split(':'))), ' '.join(message_time[1:])
        except ValueError:
            bot.send_message(message.chat.id, 'Данные введены неверно, пожалуйста, повторите все сначала')
            return
        if len(data) == 3:
            (hh, mm, ss) = data
        elif len(data) == 2:
            (hh, mm) = data
            ss = 0
        if hh > 24 or ss > 59 or mm > 59:
            bot.send_message(message.chat.id, 'Данные введены неверно, пожалуйста, повторите все сначала')
            return
        wait_rnd = Thread(target=warn, args=(bot, call.message, hh, mm, ss, True))
        wait_rnd.start()
        dngn_type = 'в ' + dngn_type if dngn_type else ''
        bot.send_message(message.chat.id, 'Таймер {}от {} установлен: '
                                          '{:02d}:{:02d}:{:02d}.'.format(dngn_type, message.json['from']['first_name'],
                                                                         hh, mm, ss))
        bot.edit_message_text('Время назначено', call.message.chat.id, call.message.message_id,
                              reply_markup=rdy_menu)

    rdy_menu = types.InlineKeyboardMarkup()
    ready = types.InlineKeyboardButton(text='Отсчет запущен', callback_data='done')
    rdy_menu.row(ready)
    blocking_menu = types.InlineKeyboardMarkup()
    block = types.InlineKeyboardButton(text='.....', callback_data='done')
    blocking_menu.row(block)
    if regular:
        hh = time_msg
        bot.edit_message_text('Время назначено', call.message.chat.id, call.message.message_id,
                              reply_markup=rdy_menu)
        wait = Thread(target=warn, args=(bot, call.message, hh))
        wait.start()
    elif not regular:
        sent = bot.send_message(call.message.chat.id, 'Установите время для запрыга в формате чч:мм:сс назначение'
                                                      ' (опционально) в reply на ЭТО сообщение')
        bot.edit_message_text('Жду ответа от пользователя', call.message.chat.id, call.message.message_id,
                              reply_markup=blocking_menu)
        bot.register_for_reply(sent, callback=set_warn)

