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
        self.counter_name = 'гильдпохода в подземелье'
        self.timeset = False
        self.timer_done = None
        self.ready30 = None
        self.message_pinned = False

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
        with open('params.json') as file:
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

        with open('params.json', 'w') as file:
            file.write(json.dumps(bot_params))

        return mm, ss, timewasset

    def _final_countdown(self):
        for i in range(3):
            n = self.send(self.chat_id, 3 - i)
            self.messages_to_delete.append(n)
            time.sleep(1)
        self.send(self.chat_id, 'Вперёд! Удачно вам сходить!')
        now = datetime.utcnow()
        final_step_time = f'{now.minute}:{now.second}.{str(now.microsecond)[:3]}'
        with open('timers.txt', 'a') as file:
            print('Таймер: {:02d}:{:02d}:{:02d} сработал в {}'.format(*self.timedata, final_step_time), file=file)
        self._clear_trash()

    def _clear_trash(self):
        if self.message_pinned:  # TODO check if deleted messages unpins
            try:
                self.bot.unpin_chat_message(self.chat_id, self.ready30.message_id)
                self.bot.unpin_chat_message(self.chat_id, self.timer_done.message_id)
            except apihelper.ApiTelegramException:
                import sys
                with open(r'unpinerrors.log', 'a') as logfile:
                    logfile.write(f'unpin messages error: {self.chat_id}\n' + format(sys.exc_info()))
        for i in self.messages_to_delete:
            time.sleep(1)
            self.bot.delete_message(self.chat_id, i.message_id)

    def _resolve_time(self):
        """
        устанавливает время для выбранного стандартного времени
        """

        self.timedata[0] = self.timer_hh_message

        if self.timer_hh_message == 12:
            self.timedata[1], self.timedata[2] = (1, 12)
        elif self.timer_hh_message == 17:
            self.timedata[1], self.timedata[2] = (1, 17)
        elif self.timer_hh_message == 21:
            self.timedata[1], self.timedata[2] = (11, 21)
            self.counter_name = 'гильдпохода в море'
        elif self.timer_hh_message == 22:
            self.timedata[1], self.timedata[2], self.timeset = self._check_22_time()
            self.timedata[0], self.timedata[1], self.timedata[2] = (18, 54, 12)

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
        self.timer_done = self.send(self.chat_id, 'Таймер для {} установлен: '
                                                  '{:02d}:{:02d}:{:02d}.'.format(self.counter_name, hh, mm, ss))
        self.bot.edit_message_text('Время назначено', self.chat_id, self.message_id,
                                   reply_markup=self.rdy_menu)
        wait = Thread(target=self._get_delta, args=self.timedata)
        wait.start()

    def _pinmessage(self):
        if self.call.message.chat.type in ['group', 'supergroup']:
            try:
                self.bot.pin_chat_message(self.chat_id, self.timer_done.message_id)
                self.message_pinned = True
            except apihelper.ApiTelegramException:
                import sys
                with open(r'unpinerrors.log', 'a') as logfile:
                    logfile.write(f'pin announce error: {self.chat_id}\n' + format(sys.exc_info()))

    def _warn_personal(self, time):
        end = {5: "5 минут", 3: "3 минуты", 2: "2 минуты", 1: "60 секунд", 30: "30 секунд"}
        with open('params.json') as file:
            bot_params = json.loads(file.read())
            warnlist = bot_params["personalwarning"][str(self.chat_id)][str(time)]
        for chat in warnlist:
            try:
                self.send(int(chat), 'Внимание, до {} в {:02d}:{:02d}:{:02d} '
                                     'осталось {}'.format(self.counter_name, *self.timedata, end[time]))
            except apihelper.ApiTelegramException:
                from settings import MY_ID
                with open("users.json") as file:
                    user_list = json.loads(file.read())
                    user = user_list[chat]
                    self.send(MY_ID, f'{user} не открыл личные сообщения')

    def _countdown(self):
        """
        Отсчет времени: оповещение за 2 минуты, за 30 сек и последние 3 сек.
        Вероятно, тут же будет реализовано оповещение по требованию в лички
        """
        if self.timedelta > 300:
            time.sleep(self.timedelta - 300)
            warn_personal = Thread(target=self._warn_personal, args=(5,))
            warn_personal.start()
            self.timedelta = 300
        if self.timedelta > 180:
            time.sleep(self.timedelta - 180)
            warn_personal = Thread(target=self._warn_personal, args=(3,))
            warn_personal.start()
            self.timedelta = 180
        if self.timedelta > 120:
            time.sleep(self.timedelta - 120)
            n = self.send(self.chat_id, 'Приготовьтесь, до {} в {:02d}:{:02d}:{:02d} '
                                        'осталось 2 минуты'.format(self.counter_name, *self.timedata))
            warn_personal = Thread(target=self._warn_personal, args=(2,))
            warn_personal.start()
            self.timedelta = 120
            self.messages_to_delete.append(n)
        if self.timedelta > 60:
            time.sleep(self.timedelta - 60)
            warn_personal = Thread(target=self._warn_personal, args=(1,))
            warn_personal.start()
            self.timedelta = 60
        if self.timedelta > 30:
            time.sleep(self.timedelta - 30)
            warn_personal = Thread(target=self._warn_personal, args=(30,))
            warn_personal.start()
            self.timedelta = 30
            self.ready30 = self.send(self.chat_id, 'Приготовьтесь, до {} в {:02d}:{:02d}:{:02d} '
                                                   'осталось 30 секунд'.format(self.counter_name, *self.timedata))
            self.messages_to_delete.append(self.ready30)

            if self.call.message.chat.type in ['group', 'supergroup']:
                try:
                    self.message_pinned = self.bot.pin_chat_message(self.chat_id, self.ready30.message_id)
                except apihelper.ApiTelegramException:
                    import sys
                    with open(r'unpinerrors.log', 'a') as logfile:
                        logfile.write(f'pin 30 error: {self.chat_id}\n' + format(sys.exc_info()))
            if self.counter_name != 'экстренного похода ':
                self._get_delta(*self.timedata, refresh=True)
            time.sleep(self.timedelta - 3)
            self._final_countdown()

        else:
            self.send(self.chat_id, 'Приготовьтесь, осталось {} секунд'.format(self.timedelta))
            time.sleep(self.timedelta - 3)
            self._final_countdown()

    def _get_delta(self, hh, mm, ss, refresh=False):
        """
        Определяет разницу времени относительно времени UTC
        Требует данных ЧЧ вo времени UTC
        """
        utc = pytz.timezone('UTC')
        now = utc.localize(datetime.utcnow())
        target_time = datetime(now.year, now.month, now.day, ((hh + 21) % 24), mm, ss, tzinfo=utc)
        time_delta = (target_time - now)
        self.timedelta = time_delta.seconds

        if refresh:
            return
        if time_delta.days < 0:
            self.send(self.chat_id, 'Предлагаю завтрашний поход объявить завтра!')
            return

        if self.timedata[0] == 22 and self.timeset:
            self.timer_done = self.send(self.chat_id, 'Сегодняшнее время гильдпохода уже было назначено на '
                                                      '{:02d}:{:02d}:{:02d}.'.format(*self.timedata))
        elif self.counter_name.startswith('гильдпохода'):
            invitetodungeon = ["Поход назначен на", "А пожалуйста!", "Есть желающие? Идём в",
                               "Не перепутайте кнопки. Сбор в"]
            self.timer_done = self.send(self.chat_id, '{} {:02d}:{:02d}:{:02d}.'.format(choice(invitetodungeon),
                                                                                        *self.timedata))
        else:
            self.timer_done = self.timer_done  # creates in resolve_user_time()
        self._pinmessage()
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
        запустить _countdown()
        очистить спам-сообщения таймера
        """
        self._hide_menu()
        if self.timer_hh_message:
            self._resolve_time()
        else:
            sent = self.send(self.chat_id, 'Установите время для похода в формате <b>ЧЧ:ММ:[СС]</b> [назначение] в '
                                           'Reply на это сообщение\n<i>(указаное внутри [ ] не обязательно)</i>',
                             parse_mode='html')

            self.bot.edit_message_text('Жду ответа от пользователя', self.chat_id,
                                       self.message_id, reply_markup=self.blocking_menu)
            self.bot.register_for_reply(sent, callback=self._resolve_user_time)

    def run_fast(self, ss):
        self._hide_menu()
        self.timedelta = ss
        self.counter_name = 'экстренного похода '
        self.timer_done = self.send(self.chat_id, f'Побежали в данжик через {ss} секунд')
        self._pinmessage()
        self._countdown()


class WarnUpdater:
    def __init__(self, bot, call, warn_time=None):
        self.time = warn_time
        self.bot = bot
        self.send = bot.send_message
        self.message = call.message
        self.user_id = str(call.from_user.id)
        self.user = call.from_user
        self.chat_id = str(call.message.chat.id)
        self.MAXLEN = 20
        self.bot_params = None
        first_name = self.user.first_name if self.user.first_name else ''
        last_name = (' ' + self.user.last_name) if self.user.last_name else ''
        self.username = first_name + last_name

    def get_group(self):
        with open('params.json', 'r') as file, open('params.json.bck', 'a') as bckfile:
            self.bot_params = json.loads(file.read())
            print(self.bot_params, file=bckfile)
            warn_list = self.bot_params["personalwarning"]
            group_list = warn_list.setdefault(self.chat_id, {'30': [], '1': [], '2': [], '3': [], '5': []})
            return group_list

    def save_params(self):
        with open('params.json', 'w') as file:
            file.write(json.dumps(self.bot_params))

    def save_user(self):
        with open('users.json', 'r+') as file:
            user_list = json.loads(file.read())
            file.seek(0)
            user_list[self.user_id] = self.username
            file.write(json.dumps(user_list))

    def set_reminder(self):
        group_list = self.get_group()
        if len(group_list[self.time]) >= self.MAXLEN:
            self.send(self.chat_id, 'Извините, очередь на это время уже переполнена, выберите другое. '
                                    'Спасибо за понимание')
            return
        for key in group_list:
            if self.user_id in group_list[key]:
                group_list[key].remove(self.user_id)
        group_list[self.time].append(str(self.user_id))
        self.save_params()
        self.save_user()
        self.send(self.chat_id, f"Оповещение для {self.username} успешно установлено на {self.time} мин.\n"
                                f"<b>Не забудьте</b> написать мне в личку любое сообщение хотя бы однажды.",
                  parse_mode='html')
        self.hide_menu()

    def remove_reminder(self):
        group_list = self.get_group()
        for key in group_list:
            if self.user_id in group_list[key]:
                group_list[key].remove(self.user_id)
        self.save_params()
        first_name = self.user.first_name if self.user.first_name else ''
        last_name = (' ' + self.user.last_name) if self.user.last_name else ''
        username = first_name + last_name
        self.send(self.chat_id, f'Оповещение для {username} отключено')
        self.hide_menu()

    def hide_menu(self):
        rdy_menu = types.InlineKeyboardMarkup()
        ready = types.InlineKeyboardButton(text='Готово', callback_data='done')
        rdy_menu.row(ready)
        self.bot.edit_message_text('Напоминание установлено', self.chat_id, self.message.id, reply_markup=rdy_menu)
