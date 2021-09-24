from datetime import datetime
from telebot import types
from time import sleep
from random import choice
from settings import DEN_ID, MY_ID, GORGONA_ID, ZST_ID
delay = 1.5


def skills_menu(bot, message):
    skill_menu = types.InlineKeyboardMarkup()
    menu_1 = types.InlineKeyboardButton(text='историю или байку', callback_data='story')
    menu_2 = types.InlineKeyboardButton(text='курсы валют', callback_data='curse')
    menu_3 = types.InlineKeyboardButton(text='данные игрока', callback_data='GV_player')
    menu_4 = types.InlineKeyboardButton(text='таймер', callback_data='timer')
    menu_5 = types.InlineKeyboardButton(text='рецепт напитка', callback_data='recipe')
    menu_6 = types.InlineKeyboardButton(text='рекомендацию фильма', callback_data='movie')
    menu_7 = types.InlineKeyboardButton(text='винную карту', callback_data='menu_bar')
    menu_8 = types.InlineKeyboardButton(text='мини-игры', callback_data='games')
    menu_9 = types.InlineKeyboardButton(text='новости футбола', callback_data='football')
    menu_close = types.InlineKeyboardButton(text='Закрыть меню', callback_data='closemenu')
    skill_menu.row(menu_1, menu_2)
    skill_menu.row(menu_3, menu_4)
    skill_menu.row(menu_5, menu_8)
    skill_menu.row(menu_9, menu_7)
    skill_menu.row(menu_6)
    skill_menu.row(menu_close)
    bot.send_message(message.chat.id, 'У нас вы можете заказать:', reply_markup=skill_menu)


def jump_menu(bot, message):
    whocan = {GORGONA_ID: 'gorgona', DEN_ID: 'den', MY_ID: 'vest', ZST_ID: "ZST"}
    keyboard = types.InlineKeyboardMarkup()
    callback_button_12 = types.InlineKeyboardButton(text='12:01:12', callback_data='прыг 12')
    callback_button_17 = types.InlineKeyboardButton(text='17:01:17', callback_data='прыг 17')
    callback_button_21 = types.InlineKeyboardButton(text='21:11:21 море', callback_data='прыг 21')
    callback_button_22 = types.InlineKeyboardButton(text='Случайное время в 22', callback_data='прыг 22')
    callback_button_xx = types.InlineKeyboardButton(text='Задайте время сами', callback_data='settime')
    callback_button_60 = types.InlineKeyboardButton(text='60 секунд', callback_data='60sec')
    callback_button_10 = types.InlineKeyboardButton(text='10 секунд', callback_data='10sec')
    keyboard.row(callback_button_12, callback_button_17)        # меню для таверны (whocan)
    keyboard.row(callback_button_22)
    keyboard.row(callback_button_21)
    keyboard.row(callback_button_10, callback_button_60)
    keyboard.row(callback_button_xx)
    keyboard_rnd = types.InlineKeyboardMarkup()                 # меню для остальных
    keyboard_rnd.row(callback_button_10)
    keyboard_rnd.row(callback_button_60)
    keyboard_rnd.row(callback_button_xx)
    if message.chat.id in whocan:
        bot.send_message(message.chat.id, 'Когда планируем поход?', reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, 'Когда планируем поход?', reply_markup=keyboard_rnd)


def games_menu(bot, message):
    game_menu = types.InlineKeyboardMarkup()
    game_button_1 = types.InlineKeyboardButton(text='Спаси Таверну', callback_data='wherewater')
    game_button_2 = types.InlineKeyboardButton(text='Крестики-нолики', callback_data='X-O')
    menu_close = types.InlineKeyboardButton(text='Не хочу играть', callback_data='closemenu')
    game_menu.row(game_button_1, game_button_2)
    game_menu.row(menu_close)
    bot.send_message(message.chat.id, 'Во что поиграем?', reply_markup=game_menu)


def bar_menu(bot, call):
    bar = types.InlineKeyboardMarkup()
    drink_1 = types.InlineKeyboardButton(text='Пиво', callback_data='пиво')
    drink_2 = types.InlineKeyboardButton(text='Вино', callback_data='вино')
    drink_3 = types.InlineKeyboardButton(text='Ламбруско', callback_data='ламбруско')
    drink_4 = types.InlineKeyboardButton(text='Сидр', callback_data='сидр')
    drink_5 = types.InlineKeyboardButton(text='Виски', callback_data='налей')
    drink_6 = types.InlineKeyboardButton(text='Коньяк', callback_data='налей')
    drink_0 = types.InlineKeyboardButton(text='На выбор бармена', callback_data='налей')
    menu_close = types.InlineKeyboardButton(text='Закрыть меню', callback_data='closemenu')
    bar.row(drink_1, drink_2, drink_3)
    bar.row(drink_4, drink_5, drink_6)
    bar.row(drink_0)
    bar.row(menu_close)
    bot.edit_message_text('Следует отметить, что бармен не очень хорошо разбирается в напитках, '
                          'поэтому почти всегда льет что попало',
                          call.message.chat.id, call.message.message_id, reply_markup=bar)


def where_is_water(bot, chat_id, gamer):
    story = ['Однажды на Таверну напал злой Бодун!',
             '\nТаверновцы посовещались и отправили самого смелого на поиски средства от него.',
             f'\nИ этот смельчак конечно же {gamer}. Запомним его именно таким!',
             '\nНо на пути к источнику лишь один путь свободен от неприятностей:',
             ' налево', ', прямо', ' или направо?',
             ]
    cave_menu = types.InlineKeyboardMarkup()
    cave1 = types.InlineKeyboardButton(text='Налево', callback_data='cave')
    cave2 = types.InlineKeyboardButton(text='Прямо', callback_data='cave')
    cave3 = types.InlineKeyboardButton(text='Направо', callback_data='cave')
    menu_close = types.InlineKeyboardButton(text='Не хочу играть', callback_data='closemenu')
    cave_menu.row(cave1, cave2, cave3)
    cave_menu.row(menu_close)
    story_message = bot.send_message(chat_id, story[0])
    for i in range(2, 8):
        sleep(delay)
        bot.edit_message_text(''.join(story[:i]), story_message.chat.id, story_message.message_id)
    sleep(delay)
    bot.send_message(chat_id, 'Какой же путь выбрать?', reply_markup=cave_menu)


def where_is_water_1(bot, message, name, way):
    story = ['На этом пути смельчака поджидал злой дракон!',
             '\nАРРРРГХ!!! КУС!! ШМЯК! ЧМЯФ!',
             f'\nНа этом приключение смельчака {name.first_name} закончилось, но через 5 минут он '
             f'снова появится на точке респауна!',
             'Что ж, путь оказался безопасен, можно идти дальше.',
             '\nИтак, впереди два источника, каждый из которых подозрительно похож на святой',
             ', но лишь в одном из них спасительный рассол.',
             '\nИз какого же источника набрать бочонок для страдающей гильдии?'
             ]
    if not way:
        story_message = bot.send_message(message.chat.id, story[0])
        for i in range(2):
            sleep(delay)
            bot.edit_message_text(''.join(story[:2 + i]), story_message.chat.id, story_message.message_id)
            if message.chat.type == 'supergroup':
                administrators = [admin.user.id for admin in bot.get_chat_administrators(story_message.chat.id)]
                if name.id not in administrators:
                    # bot.restrict_chat_member(story_message.chat.id, name.id,
                    #                        until_date=datetime.now() + timedelta(minutes=5), can_send_messages=False)
                    chat_id = story_message.chat.id
                    user_id = name.id
                    clock = datetime.now().timestamp() + 300
                    import requests
                    import json
                    req = f'https://api.telegram.org/bot{bot.token}/restrictChatMember'
                    permissions = {'can_send_messages': False, 'can_invite_users': True, 'can_change_info': True,
                                   'can_pin_messages': True}
                    permissions_json = json.dumps(permissions)
                    params = {'chat_id': chat_id, 'user_id': user_id, 'permissions': permissions_json,
                              'until_date': clock}
                    try:
                        requests.post(req, json=params)
                    except:
                        pass
    else:
        cave_menu = types.InlineKeyboardMarkup()
        cave1 = types.InlineKeyboardButton(text='Левый', callback_data='rassol')
        cave2 = types.InlineKeyboardButton(text='Правый', callback_data='rassol')
        menu_close = types.InlineKeyboardButton(text='Не хочу играть', callback_data='closemenu')
        cave_menu.row(cave1, cave2)
        cave_menu.row(menu_close)
        story_message = bot.send_message(message.chat.id, story[3])
        for i in range(2):
            sleep(delay)
            bot.edit_message_text(''.join(story[3:5 + i]), story_message.chat.id, story_message.message_id)

        sleep(delay)
        bot.send_message(message.chat.id, story[6], reply_markup=cave_menu)


def cross_zeros(bot, call, message_to_del, state):
    top_message = 'Ну что ж, начнем' if 'O' not in state else 'Я сделал свой ход'
    top_message = 'Игра окончена' if '*' in state or ' ' not in state else top_message
    bot.delete_message(call.message.chat.id, message_to_del)
    xo_menu = types.InlineKeyboardMarkup()
    button_1 = types.InlineKeyboardButton(text=state[0], callback_data='xo0')
    button_2 = types.InlineKeyboardButton(text=state[1], callback_data='xo1')
    button_3 = types.InlineKeyboardButton(text=state[2], callback_data='xo2')
    button_4 = types.InlineKeyboardButton(text=state[3], callback_data='xo3')
    button_5 = types.InlineKeyboardButton(text=state[4], callback_data='xo4')
    button_6 = types.InlineKeyboardButton(text=state[5], callback_data='xo5')
    button_7 = types.InlineKeyboardButton(text=state[6], callback_data='xo6')
    button_8 = types.InlineKeyboardButton(text=state[7], callback_data='xo7')
    button_9 = types.InlineKeyboardButton(text=state[8], callback_data='xo8')
    menu_close = types.InlineKeyboardButton(text='Не хочу играть', callback_data='closemenu')
    xo_menu.row(button_1, button_2, button_3)
    xo_menu.row(button_4, button_5, button_6)
    xo_menu.row(button_7, button_8, button_9)
    xo_menu.row(menu_close)
    sleep(0.1)
    send = bot.send_message(call.message.chat.id, top_message, reply_markup=xo_menu)
    return send.message_id


def xo_any_wins(bo, le):
    return ((bo[6] == le and bo[7] == le and bo[8] == le) or
            (bo[3] == le and bo[4] == le and bo[5] == le) or
            (bo[0] == le and bo[1] == le and bo[2] == le) or
            (bo[6] == le and bo[3] == le and bo[0] == le) or
            (bo[7] == le and bo[4] == le and bo[1] == le) or
            (bo[8] == le and bo[5] == le and bo[2] == le) or
            (bo[6] == le and bo[4] == le and bo[2] == le) or
            (bo[8] == le and bo[4] == le and bo[0] == le))


def xo_end_game(state):
    # проверка на победу кого-либо
    if xo_any_wins(state, 'X') or xo_any_wins(state, 'O'):
        for i in range(9):
            if state[i] == ' ':
                state[i] = '*'
    return state


def xo_bot_move(state):
    # проверка на победу бота следующим ходом
    for i in range(9):
        state_copy = state.copy()
        if state_copy[i] == ' ':
            state_copy[i] = 'O'
            if xo_any_wins(state_copy, 'O'):
                state[i] = 'O'
                return state

    # проверка на победу игрока и блокировка этого хода
    for i in range(9):
        state_copy = state.copy()
        if state_copy[i] == ' ':
            state_copy[i] = 'X'
            if xo_any_wins(state_copy, 'X'):
                state[i] = 'O'
                return state

    # Занимаем центр
    if state[4] == ' ':
        state[4] = 'O'
        return state

    # Пробуем занять один из углов, если есть свободные.
    possible = []
    for i in [0, 2, 6, 8]:
        if state[i] == ' ':
            possible.append(i)
    if possible:
        state[choice(possible)] = 'O'
        return state

    # Делаем ход по одной стороне.
    possible = []
    for i in [1, 3, 5, 7]:
        if state[i] == ' ':
            possible.append(i)
    if possible:
        state[choice(possible)] = 'O'
        return state
    return state
