import json
import time
from random import randint, choice
import pytz
from datetime import datetime
from telebot import types, apihelper
from threading import Thread


class CounterJump:
    def __init__(self, bot, call, timer_message=None):
        # Thread.__init__(self)

        self.timer_hh_message = timer_message
        self.bot = bot
        self.send = bot.send_message
        self.call = call
        self.chat_id = call.message.chat.id
        self.message_id = self.call.message.message_id
        self.timedelta = 0
        self.timedata = [0, 0, 0]  # hh, mm, ss
        self.messages_to_delete = []
        self.counter_name = 'гильдпоход в подземелье'

    def _hide_menu(self):
        self.rdy_menu = types.InlineKeyboardMarkup()
        ready = types.InlineKeyboardButton(text='Отсчет запущен', callback_data='done')
        self.rdy_menu.row(ready)
        self.blocking_menu = types.InlineKeyboardMarkup()
        block = types.InlineKeyboardButton(text='.....', callback_data='done')
        self.blocking_menu.row(block)
        self.bot.edit_message_text('Время назначено', self.chat_id, self.message_id,
                                   reply_markup=self.rdy_menu)

    def _check_22_time(self):
        """
        Проверяет, было ли уже выбрано время в 22ч на случай перезапуска бота
        """
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

    def _final_countdown(self):
        for i in range(3):
            n = self.send(self.chat_id, 3 - i)
            self.messages_to_delete.append(n)
            time.sleep(1)
        utc = pytz.timezone('UTC')
        now = utc.localize(datetime.utcnow())
        data = str(now.minute) + ":" + str(now.second)
        print(data)             # TODO log for delay check
        self.send(self.chat_id, 'Вперёд! Удачно вам сходить!')
        self._clear_trash()

    def _clear_trash(self):
        for i in self.messages_to_delete:
            time.sleep(1)
            self.bot.delete_message(self.chat_id, i.message_id)

    def _resolve_time(self):
        """
        устанавливает время для выбранного стандартного времени
        """

        self.timedata[0] = self.timer_hh_message
        timeset = False
        if self.timer_hh_message == 12:
            self.timedata[1], self.timedata[2] = (1, 12)
        elif self.timer_hh_message == 17:
            self.timedata[1], self.timedata[2] = (1, 17)
        elif self.timer_hh_message == 22:
            self.timedata[1], self.timedata[2], timeset = self._check_22_time()
        if timeset:
            self.send(self.chat_id, 'Сегодняшнее время гильдпохода уже было назначено на '
                                    '{}:{:02d}:{:02d}.'.format(*self.timedata))
        else:
            invitetodungeon = ["Поход назначен на", "А пожалуйста!", "А пойдемте в данж! В",
                               "Не перепутайте кнопки. Сбор в"]
            self.send(self.chat_id, '{} {}:{:02d}:{:02d}.'.format(choice(invitetodungeon), *self.timedata))
        wait = Thread(target=self._get_delta, args=self.timedata)
        wait.start()

    def _resolve_user_time(self, message):
        hh, mm, ss = (0, 0, 0)
        try:
            message_time = message.text.split() + ['']
            data, dngn_type = list(map(int, message_time[0].split(':'))), ' '.join(message_time[1:])
            if len(data) == 3:
                (hh, mm, ss) = data
            elif len(data) == 2:
                (hh, mm) = data
                ss = 0
            elif len(data) == 1:
                self.send(self.chat_id, 'Задайте часы и минуты, пожалуйста, повторите все сначала')
                return
            if hh > 23 or ss > 59 or mm > 59:
                raise ValueError
        except ValueError:
            self.send(self.chat_id, 'Данные введены неверно, пожалуйста, повторите все сначала')
            return

        self.timedata = [hh, mm, ss]
        dngn_type = 'в ' + dngn_type if dngn_type else ''
        self.counter_name = 'похода {}с {}'.format(dngn_type, message.json['from']['first_name'])
        self.send(self.chat_id, 'Таймер для {} установлен: {:02d}:{:02d}:{:02d}.'.format(self.counter_name, hh, mm, ss))
        self.bot.edit_message_text('Время назначено', self.chat_id, self.message_id,
                                   reply_markup=self.rdy_menu)
        wait = Thread(target=self._get_delta, args=self.timedata)
        wait.start()

    def _warn_two_minutes(self):
        pass            # TODO check delay!

    def _countdown(self):
        """
        Отсчет времени: оповещение за 2 минуты, за 30 сек и последние 3 сек.
        Вероятно, тут же будет реализовано оповещение по требованию в лички
        """
        if self.timedelta > 120:
            time.sleep(self.timedelta - 120)
            n = self.send(self.chat_id, f'Приготовьтесь, до {self.counter_name} осталось 2 минуты')
            self._warn_two_minutes()
            self.timedelta = 120
            self.messages_to_delete.append(n)
        if self.timedelta > 30:
            time.sleep(self.timedelta - 30)
            self.timedelta = 30
            ready30 = self.send(self.chat_id, f'Приготовьтесь, до {self.counter_name} осталось 30 секунд')
            self.messages_to_delete.append(ready30)
            message_pinned = False
            if self.call.message.json['chat']['type'] in ['group', 'supergroup']:
                try:
                    self.bot.pin_chat_message(self.chat_id, ready30.message_id)
                    message_pinned = True
                except apihelper.ApiTelegramException:
                    import sys
                    with open(r'unpinerrors.log', 'a') as logfile:
                        logfile.write(format(sys.exc_info()[0]))
            # self._get_delta(*self.timedata)       # TODO refresh delta - ПРИЧИНА ДВОЙНОГО СЧЕТА
            time.sleep(self.timedelta - 3)
            self._final_countdown()
            if message_pinned:
                try:
                    self.bot.unpin_chat_message(self.chat_id, ready30.message_id)
                except apihelper.ApiTelegramException:
                    import sys
                    with open(r'unpinerrors.log', 'a') as logfile:
                        logfile.write(format(sys.exc_info()[0]))
        else:
            self.send(self.chat_id, 'Приготовьтесь, осталось {} секунд'.format(self.timedelta))
            time.sleep(self.timedelta - 3)
            self._final_countdown()

    def _get_delta(self, hh, mm, ss):
        """
        Определяет разницу времени относительно времени UTC
        Требует данных ЧЧ вo времени UTC
        """
        utc = pytz.timezone('UTC')
        now = utc.localize(datetime.utcnow())
        target_time = datetime(now.year, now.month, now.day, ((hh + 21) % 24), mm, ss, tzinfo=utc)
        time_delta = (target_time - now)
        if time_delta.days < 0:
            self.send(self.chat_id, 'Предлагаю завтрашний поход объявить завтра!')
            return
        else:
            self.timedelta = time_delta.seconds
            self._countdown()

    def run(self):
        """
        свернуть менюшку ==> _hidemenu()
        Получить команду: 17, 12, 22 или settime (60 / 10 позднее)  ==> _resolve_time()
        обработать команду и получить итоговое время
            - проверить 12 или 17 ==> готовое время
            - проверить 22 ==>      _check_22_time()
            - получить пользовательский таймер
            - обработать 60 сек, 10 сек
        посчитать delta ==> _getdelta ()
        запустить _countodwn()
        очистить спам-сообщения таймера
        """
        self._hide_menu()
        if self.timer_hh_message:
            self._resolve_time()
        else:
            sent = self.send(self.chat_id, 'Установите время для запрыга в формате <b>ЧЧ:ММ:[СС]</b> [назначение] в '
                                           'Reply на это сообщение\n<i>(указаное внутри [ ] не обязательно)</i>',
                             parse_mode='html')

            self.bot.edit_message_text('Жду ответа от пользователя', self.chat_id,
                                       self.message_id, reply_markup=self.blocking_menu)
            self.bot.register_for_reply(sent, callback=self._resolve_user_time)
