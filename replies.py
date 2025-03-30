from random import choice
import time
from settings import CHATBOT_TOKEN as chatbot_token

last_drink = 0

alko = ['CAACAgEAAxkBAAICgF6oCcIsaCSU6us8r1QZvWXLlXtHAAI2CAACv4yQBGnvTm8BVH2EGQQ',      # бородач       0 пивные
        'CAACAgIAAxkBAAIBoF6nGX93X0vEnB4Oa3E0ZlIBb725AAJ9CAACCLcZAunMCcpewSH8GQQ',      # godofwar      1
        'CAACAgIAAxkBAAICgV6oCfW0ePXUGi7BKuCnTJ8ewAHHAAIvAAOvxlEa-NtBblWpkVsZBA',       # улитка        2
        'CAACAgIAAxkBAAICy16oHczuxPssB2HSsZDSTWzVEJiTAAKJBQAClvoSBYtPxYQyKuLyGQQ',      # viking beer       3
        'CAACAgIAAxkBAAIJHl6tspnmAAGQ9orP1hQhLkdhO7eIIwACrgIAAlv_8go7RcMC73c8mxkE',     # beerman head over 4
        'CAACAgIAAxkBAAICv16oG0zFM0sYVsdgA2iV4zLtnGKOAAKoAgACW__yCl703BtCE6LzGQQ',      # beerman pssst     5
        'CAACAgIAAxkBAAICu16oGsrCCjBxUcUEcpIf5zAU1ZlJAAKfAgACW__yCk1AiWUF4XYOGQQ',      # beerman juggler   6
        'CAACAgIAAxkBAAPEXqX9mNtBuBaZDbslRTvQoYVP8AAD4AYAAvoLtghhj6hIGFRhGBkE',         # собаки бешенные   7
        'CAACAgEAAxkBAALepWAz1LqtC8Mk7nyiUp0Unzc-gm0UAAJWAQACXiwsBB-eBbDn5lPXHgQ',      # пьяная рысь       8
        'CAACAgIAAxkBAAPUXqX-F_CahpH_XX13uf5uoCWLv30AAnQAA5i_gA3AdesOfYN5gxkE',         # кошка             9 винные +др
        'CAACAgIAAxkBAAPWXqX-P1-HaAdo2I0U3j5vR1rkDgMAAt4AA1advQql73c4VYMVxBkE',         # телесобачка
        'CAACAgIAAxkBAAPDXqX9kCuutKW1OWks7muDCwuEYQsAAr4AA5zW5woDa9z_qaorhBkE',         # динобармен
        'CAACAgIAAxkBAAPXXqX-cCgdLEvcGUiM8d6x2gEqPHoAAuUFAAKW-hIFIupdSHfdpZIZBA',       # шейх
        'CAACAgIAAxkBAAICuV6oGht2jy_K3sEVoa62Aw4x0NqsAAKwAgACW__yCrY3JODCJrmbGQQ',      # beerman boring
        'CAACAgIAAxkBAAICul6oGlTaP6eaZib9EVsQ0CSyovI6AAKvAgACW__yCpGjCnlbto0nGQQ',      # beerman double
        'CAACAgIAAxkBAAICvF6oGvXHQr4wzqb-1Uqy9qCZq_xEAAKtAgACW__yCsyD7ff_xiVmGQQ',      # beerman mixing
        'CAACAgIAAxkBAALet2Az1wtSYN6EhHwRI6gZ1dGMM7EQAAKkAgACW__yCnIQAd7UjqszHgQ',      # beerman jesus
        'CAACAgIAAxkBAAICzF6oHe7K2eJYvitHPX0WomUOIfB_AAKCBQAClvoSBXG7XPY1_q_rGQQ',      # viking vine
        'CAACAgIAAxkBAAIC216oIo9nN_hqhol7n49VRwRZbqtqAAIhAANf-4UVTeD-5ljFw2EZBA',       # snail gentleman
        'CAACAgIAAxkBAAIMJF65jqu15UFvKpSBPtZa_PhnWf7lAAIoAAMoD2oUkEu3yx5vAxAZBA',       # бокал с кошкой
        'CAACAgIAAxkBAAIMJV65jt1GI-kevvgHyN9Da-YkDWepAAIsAgACz7vUDnWyGzZVIZerGQQ',      # бокал со змеей
        'CAACAgIAAxkBAAIMJl65jv0KCL4yveBn7fZ0Ld019QmDAALyAgAC73cHAAGUblmkID-I2xkE',     # ром остров сокровищ
        'CAACAgIAAxkBAAIMJ165jyN-FHkHchGyp7uhlCyWD-QOAAJWAANEDc8XGUGSGSyvU3cZBA',       # собачка с бокалами
        ]

spirt = ['CAACAgIAAxkBAAII42FEpSAO3kmXJ0OqAAFQj1b3l_IqDQACZhAAApO8-EmMjC2KIB7StSAE',    # клизьма
         'CAACAgIAAxkBAAII8GFEpiLUaoUvIuSCp4YoyW43vXdiAAIKAAP-GKoTLvJgGu1w56UgBA',      # chemistry brandon
         'CAACAgIAAxkBAAII-2FEp4fSCCwKSSokwcZB9nYoaDneAAJIFAACY4tGDNcMsdNoe2_iIAQ',     # alkoholizm
         'CAACAgIAAxkBAAII_GFEqO454yrD-4McejRTOQt6143HAAJTAwACDDsAAQpuqbY1uUV7HCAE',    # razveli tut
         ]

owlstiker = ['CAACAgIAAxkBAAIBDV6mAAG-Pl8AAWnSZDvHgUz81ww5p2IAAkwAA3FwZwQygrCaXSZHYhkE',    # сова ламбруско
             'CAACAgIAAxkBAAIC3V6oK2Wr3EsDl_zcbaUw_fR2Vn05AALtAANr7XwK1YxMfEd8EAUZBA',      # сова с пивом
             'CAACAgIAAxkBAAIDHl6oLiQS0mm8TV3RC6JBi9CQKLZNAALEAQACGELuCNMqsp36EbLVGQQ',     # сова с вином
             'CAACAgIAAxkBAAP1XqX_zsMyJjH84e8d7Gf-tNxp9XUAAjIAA8GcYAwHIPxp5MyzxRkE',        # сова с мобилой
             'CAACAgIAAxkBAAIDeV6oOUtqkMcEOFx67kA3sfgOIBqYAAJuAAMYQu4IpymFR7sasEoZBA',      # сова бубубу
             ]

snake = ["Шшшшшшшш-шшшш-шшш 🐍", "Шшшшшшшто вы говорите?", "А змеюк покормили?",
         "Рад видеть всех вас, змейки!", "Тут есть змееуст?"
         ]
lapki = ["*жмяк лапки*", "🐾", "🐾🐾",  "🐾🐾🐾", "🐾🐾🐾🐾",
         "Этот тип подлый и мерзкий! Он мой лучший друг, да.",
         "Этот заговор серьёзнее, чем я представлял в своих самых диких параноидальных снах.",
         "И где наш монохромный соратник?"]

zakus = ["Закусывайте, закусывайте! Не частите!", "А закусывать кто будет?",
         "А вам есть 18?", "Мне кажется, что Вам пока хватит."]

bothere = ["Я здесь!", "Чего изволите?", "Это я. Как поживаете?", "Да-да?",
           "Нет, увы.", "Вовсе нет.", "Нет меня.", "Отнюдь!", "Шо, опять?!", "Ну конечно же!",
           "Не отвлекайте, пожалуйста! Я же занят!", "Ах, оставьте!", "Хотите взгляд, полный понимания?",
           "Кажется, я случайно переделал ваш коктейль в безалкогольный…",
           "Я не пью, я проверяю качество напитка!", "Не откажусь с вами выпить за ваш счёт.",
           "Вчера я унёс пару бутылок «Westvleteren 12», чтобы показать своим друзьям и вернуть обратно.",
           "Не злите бармена – налью «Боржоми».", "Бармен всегда и во всём прав!",
           "Лед в стакане шепчет тайны. Слушает только бармен.",
           "Бармены не делают ошибок, они создают новые рецепты.",
           "Смешать, встряхнуть, украсить — и вот магия готова!",
           "Если у тебя плохой день, бармен знает, как сделать его хуже… или лучше.",
           "Бармены знают, кто из гостей уйдёт с бокалом, а кто с улыбкой.",
           "Бармен видит всех: от любителей поговорить до мастеров исчезнуть.",
           "Я не просто наливаю напитки, я создаю воспоминания."]

payment = ["Стоять за стойкой одно удовольствие! А не стоять - другое.",
           '*достает банку с надписью "Чаевые Арчи"*',
           '*с грустью смотрит на банку с надписью "Чаевые Арчи"*',
           "Оплата? Не, не слышал", "Деньги - зло! И мне на все зла не хватает!"]

def check_group(message):
    from re import findall
    group = findall(r'групп.* ([a-zа-я])', message)
    dict_translate = str.maketrans('абсдефгхи', 'abcdefghi')
    if group:
        group = group[0].translate(dict_translate)
        return group.upper()
    else: return None


def reply(message):
    from re import findall
    seller_name, seller_id, message_date, chat_is_private = ('', 0, time.time(), False)
    if type(message) != str:
        seller_name = message.json["from"]["first_name"]
        seller_id = message.json["from"]["id"]
        message_date = message.json['date']
        chat_is_private = message.json['chat']['type'] == 'private'
        message = message.text.lower()
    else:
        message = message.lower()

    re_phrases = {
        'tea_coffee': r'\bча[йюя]|\bкофе|\bкомпот',
        'juice': r'\bсок[ау]?\b',
        'wanttodrink': r'\bнал(|ив)([еа])+й\b|\bплесн(и|у)',
        'beer': r'\bпив(о|а|ка)|\bсидр|\bпенно(е|го)\b',
        'owl': r'\bс[оа]ва\b',
        'gorgosha': r'\bгорго[шн]',
        'vestenar': r'\bvestenar|\bвестенар|\bвест\b',
        'kitty': r'\bм[я]+[укф]+\b',
        'c2h5oh': r'\bспирт[ау]?\b|c2h5oh',
        'wine': r'\bвин(ц|ишк)?[оау]\b|\bконья.*к|\bвиск(и|арик)|\bром[ау]?\b|\bвод(к|очк)[аиу]|ламбрус',
        'vsegun': r'вс[её]гун',
        'hello': r'привет|\bхай|\bздрям|здравствуй|(добр(ый|ого|ое)( утр[оа]|( день| дня)| вечер[а]| времени))',
        'masshello': r'всем (привет|хай|здрям|здравствуй|(добр(ый|ого|ое) (утр[оа]|(день|дня)|вечер[а]|времени)))',
        'byebye': r'всем (\bпока\b|спокойной ночи|снов|до (встреч|свидания|завтра))',
        'botname': r'\bбот[ауе]?|бармен|хозяин|арчи(|бальд)?[о]?|oldtavern_bot',
        'botpay': r'\bплат[ия]т|\b(о|зар)плат',
        'tellstory': r'(расскажи|поведай|мы хотим|\bтрав(и|ани)).*(истори[яюий]|байк[иу]|анекдот)|(раз|по)весели',
        'movie': r'\bчто .*посмотреть|(фильм|кино).*(посоветуй|како|посмотреть)|'
                 r'(посоветуй|како|посмотреть).*(фильм|кино)',
        'obida': r'\bдура(к|цкий)|\bтуп(ой|ая)\b|\bидиот|глуп(ая|ый)|херов(ый|ая)|хренов(а|ая|ый)',
        'valutes': r'на биржах|курс(ы|ах) валют|что почем|куда вкладывать',
        'player': r'(расскажи|что знаешь|что слышал|шепни|какие слухи) (о|про)',
        'recepie': r'(научи|дай|поделись|.*скажи).*(готовить|рецепт)',
        'football_euro': r'лиг.+ европы',
        'football_champ': r'лиг.+ чемпионов',
        'football_konference': r'лиг.+ конференц',
        'football_world': r'чемпион.+ мира|чм.{0,3}22'
    }
    found_phrases = []

    for phrase in re_phrases:
        if findall(re_phrases[phrase], message):
            found_phrases.append(phrase)
    if chat_is_private:
        found_phrases.append('botname')
    findall = None

    miau = ['Мяу! Чего б и не мяукнуть по пьяни, да?', 'МЯУ! Так надо?',
            'Кто это там у нас мяучит?', 'Кис-кис-кис, {}.'.format(seller_name)
            ]

    greetings = ["Доброго времени суток, {}!".format(seller_name),
                 "Привет-привет!", "Здравствуйте! Чем могу быть полезен?",
                 "Бонжур! Же не манж па сис жюр? Что бы это ни значило."
                 ]

    otvetka = ["Уважаемый, попридержите коней!", "А если вышибалу позову?",
               "Сам такой, {}!".format(seller_name),
               "Что-то посетители расшумелись, пора закрываться.",
               "А не пора ли вам по койкам, господа хорошие?",
               "В бою с боссом будешь выпендриваться, {}, а тут соблюдай приличия.".format(seller_name),
               ]

    global last_drink

    if 'obida' in found_phrases:
        return choice(otvetka), 'text'
    if 'masshello' in found_phrases or ('hello' in found_phrases and 'botname' in found_phrases):
        return choice(greetings), 'text'
    if 'byebye' in found_phrases:
        return "Всего хорошего", 'text'
    if 'botname' in found_phrases and 'tellstory' in found_phrases:
        from getinfo import get_story
        return get_story(), 'text'
    if 'botname' in found_phrases and 'movie' in found_phrases:
        from getinfo import get_movie
        return get_movie(), 'text'
    if 'botname' in found_phrases and 'recepie' in found_phrases:
        from getinfo import get_recepie
        return 'Кто-то спер поваренную книгу! (На самом деле нет, когда-нибудь будет поправлено)', 'text'
        # return get_recepie(), 'img'
    if 'botname' in found_phrases and 'valutes' in found_phrases:
        from getinfo import get_currencies
        return get_currencies(), 'text'
    if 'botname' in found_phrases and 'football_euro' in found_phrases:
        from getinfo import get_football
        group = check_group(message)
        return get_football('euro', group), 'text'
    if 'botname' in found_phrases and 'football_champ' in found_phrases:
        from getinfo import get_football
        group = check_group(message)
        return get_football('champ', group), 'text'
    if 'botname' in found_phrases and 'football_konference' in found_phrases:
        from getinfo import get_football
        group = check_group(message)
        return get_football('konf', group), 'text'
    if 'botname' in found_phrases and 'football_world' in found_phrases:
        from getinfo import get_football
        group = check_group(message)
        return get_football('world', group), 'text'

    if 'botname' in found_phrases and 'botpay' in found_phrases:
        return choice(payment), 'text'
    if 'owl' in found_phrases and 'wanttodrink' in found_phrases:
        last_drink = message_date
        return choice(owlstiker[:3]), 'sticker'
    if 'owl' in found_phrases:
        return choice(owlstiker[1:]), 'sticker'
    if 'wine' in found_phrases:
        if message_date - last_drink >= 10:
            last_drink = message_date
            return choice(alko[9:]), 'sticker'
        else:
            return choice(zakus), 'text'
    if 'beer' in found_phrases:
        if message_date - last_drink >= 10:
            last_drink = message_date
            return choice(alko[:9]), 'sticker'
        else:
            return choice(zakus), 'text'
    if 'c2h5oh' in found_phrases:
        return choice(spirt), 'sticker'
    if 'tea_coffee' in found_phrases:
        answer = ['Хотите этого? Может чего покрепче?', 'С сушками, ага, конечно',
                  'С сушками и копчеными эльфьими ушками', 'Щяс, набадяжу.']
        return choice(answer), 'text'
    if 'juice' in found_phrases:
        answer = ['Сооок? Ну это только для избранных! И только вишнёвый.',
                  'Сок - это как вино, только без градуса? Есть, конечно.',
                  '*достает именной стакан*']
        return choice(answer), 'text'
    if 'wanttodrink' in found_phrases:
        if message_date - last_drink >= 10:
            last_drink = message_date
            return choice(alko), 'sticker'
        else:
            return choice(zakus), 'text'

    if 'себе' not in message and 'player' in found_phrases:
        from getgodville import god_info
        message = message.replace(' про ', ' о ')
        playername = message.split(' о ')[-1].split(',')[0].split('?')[0].split('.')[0].split('!')[0].strip()
        return god_info(playername), 'text'
    if 'gorgosha' in found_phrases:
        return choice(snake), 'text'
    if 'vestenar' in found_phrases:
        return choice(lapki), 'text'
    if 'kitty' in found_phrases:
        return choice(miau), 'text'
    if 'vsegun' in found_phrases:
        return 'Снимите с него шкуру!', 'text'
    if 'botname' in found_phrases:
        # from chatbot import dialog_flow
        # for name in ['бот', 'бармен', 'арчибальд', 'арчи', 'арчибль']:
        #     message = message.replace(name, ' ').strip()
        # try_ans = dialog_flow(message, chatbot_token)
        # dialog_flow = None
        try_ans = None      # в связи с изменениями в DialogFlow
        if try_ans:
            return try_ans, 'text'
        else:
            return choice(bothere), 'text'
    return None, None


if __name__ == '__main__':
    # import json
    # with open('params.txt') as init_file:
    #     bot_params = json.loads(init_file.read())
    #     chatbot_token = bot_params["chatbot_token"]

    while True:
        msg = input()
        print(reply(msg))
