import requests
from json import loads
from random import randint
from bs4 import BeautifulSoup


def get_currencies():
    currencies = []
    cbcurs = requests.get('https://www.cbr-xml-daily.ru/daily_json.js')
    currency_cb = loads(cbcurs.text)
    currencies.append('1 USD 💵:         {} рублей'.format(currency_cb['Valute']['USD']['Value']))
    currencies.append('1 EUR 💶:         {} рублей'.format(currency_cb['Valute']['EUR']['Value']))
    godcurs = requests.get('https://godville.net/news')
    soup = BeautifulSoup(godcurs.text, 'lxml')
    kotirs = soup.find('div', {'class': 'rate clearfix'})
    currencies.append('1 босскоин 🧿:  ' + kotirs.contents[5].contents[0] + '💰')
    currencies.append('1 кирпич 🧱:     ' + kotirs.contents[9].contents[0] + '💰')
    currencies.append('1 инвайт 🔖:     ' + kotirs.contents[13].contents[0] + '💰')
    cbcurs = None
    godcurs = None
    soup = None
    kotirs = None
    return 'Курсы валют на текущий момент:\n\n' + '\n'.join(currencies)


def get_story():
    url = 'http://lolstory.ru/story/'
    antimat = 'Возможна ненормативная лексика. ' \
              'Чтобы увидеть слово отключите цензор в низу страницы и обновите страницу. '
    MAXLEN = 1000
    for _ in range(10):
        number = randint(1, 14950)
        get_url = url + str(number)
        resp = requests.get(get_url)
        if resp.status_code != 200:
            return 'Устал я сегодня, да и память уже не та'

        soup = BeautifulSoup(resp.content, 'lxml')
        story = soup.find('div', {'class': 'post-text'})
        if story and len(story.text) <= MAXLEN:
            return story.text.strip().replace('\n\r', '\n').replace(antimat, '')
        soup = None
        story = None
    return 'Что-то в памяти всплывают только длинные истории, не хочется вас ими утруждать'


def get_movie():    # TODO доделать парсинг сайта под ajax или найти другой источник
    url = 'https://www.kinomania.ru/top/films'
    headers = {'User-Agent': 'Mozilla/5.0', 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
    session = requests.Session()
    resp = session.get(url, headers=headers)
    if resp.status_code != 200:
        return 'Да какие фильмы? Работать нужно'
    cookies = requests.utils.cookiejar_from_dict(requests.utils.dict_from_cookiejar(session.cookies))
    headers = {'User-Agent': 'Mozilla/5.0',
               'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
               'X-Requested-With': 'XMLHttpRequest'}
    url = 'https://www.kinomania.ru/top/films?handler=search'
    resp = session.post(url, headers=headers, cookies=cookies)
    session.close()
    if resp.status_code != 200:
        return 'Да какие фильмы? Работать нужно'
    data = loads(resp.text)
    resp = None
    position = randint(0, 99)
    data = data[position]

    return 'Нууу, например... "{}".\nРейтинг: {}. Позиция в рейтинге: {}.'.format(data['name_ru'],
                                                                                  data['rate'], position + 1)


def get_recepie():      # TODO найти другой источник, не такой корявый
    page = randint(1, 49)
    url = 'https://www.povarenok.ru/recipes/category/20/~{}/?sort=rating&order=desc'.format(page)
    resp = requests.get(url)
    if resp.status_code != 200:
        return 'А я уже все замешал и так', '', None
    soup = BeautifulSoup(resp.text, 'lxml')
    recepies = soup.find_all('article', {'class': 'item-bl'})

    showrec = randint(0, 14)
    recepie_link = recepies[showrec].contents[1].contents[1]['href']
    recepie_name = recepies[showrec].contents[3].contents[1].text
    recepie_picture = recepies[showrec].contents[5].contents[1].contents[1]['src']

    resp_chosen = requests.get(recepie_link)
    if resp.status_code != 200:
        return 'А я уже все замешал и так', '', None

    soup = BeautifulSoup(resp_chosen.text, 'lxml')
    ingridients = soup.find('div', {'class': 'ingredients-bl'})

    ingr_list = ['Нам понадобятся:']
    for i in range(1, len(ingridients.contents[1].contents), 2):
        name = ingridients.contents[1].contents[i].contents[1].contents[1].text.strip()
        if len(ingridients.contents[1].contents[i].contents[1].contents) > 3:
            quantity = ingridients.contents[1].contents[i].contents[1].contents[3].text.strip()
        else:
            quantity = ''
        ingr_list.append(name + ':  ' + quantity)
    ingridients = '\n'.join(ingr_list)

    preparation = soup.find_all('div', {'class': 'cooking-bl'})
    text = ''
    if preparation:
        for point in preparation:
            text += point.text.strip() + '\n'
    else:
        preparation = soup.find('article', {'class': 'item-bl item-about'})
        for i in range(34, 38):
            if preparation.contents[1].contents[i].name == 'div':
                text = preparation.contents[1].contents[i].text
                break

    first_text = '{}\n\n{}'.format(recepie_name, ingridients)
    soup = None
    resp = None
    resp_chosen = None
    preparation = None
    ingridients = None
    return first_text, text, recepie_picture


def get_football(league, group=None):
    parts, games, url = [], [], ''
    if league == 'champ':
        url = 'https://terrikon.com/champions-league/'
        # name = 'Чемпионов'
        parts = ['1/8 финала', '1/4 финала', '1/2 финала', 'Финал']
    elif league == 'euro':
        url = 'https://terrikon.com/europa-league/'
        # name = 'Европы'
        parts = ['1/8 финала', '1/4 финала', '1/2 финала', 'Финал']
    elif league == 'konf':
        url = 'https://terrikon.com/conference-league/'
        parts = ['1/8 финала', '1/4 финала', '1/2 финала', 'Финал']
    elif league == 'world':
        url = 'https://terrikon.com/worldcup-2022/'
        parts = ['1/8 финала', '1/4 финала', '1/2 финала', 'Финал']
    headers = {'User-Agent': 'Mozilla/5.0', 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
    session = requests.Session()
    resp = session.get(url, headers=headers)
    session.close()
    if resp.status_code != 200:
        return 'Какой такой футбол еще?'
    soup = BeautifulSoup(resp.text, 'lxml')
    name = soup.find('h1').text
    # table = f'Лига {name} 2020/21. '
    table = name + ' \n'
    # parts = {3: '1/8 финала', 2: '1/4 финала', 1: '1/2 финала', 0: 'Финал'}

    if not group:
        for part in parts:
            # games = soup.find_all('table', {'class': 'gameresult'})[part]
            games = soup.select_one(f'h2:-soup-contains("{part}")')
            if not games:
                return table + f'игры {parts[0]} еще не начались'
            games = games.find_next('table')
            if '-:-' in games.text:
                table += part + '\n\n'
                break
    else:
        table += f'Группа {group}\n\n'
        games = soup.select_one(f'h2:-soup-contains("{group}")').find_next('table', {'class': 'gameresult'})
        if not games:
            return table + f'Группа {group} в турнире не найдена'

    for game in games:
        if game != '\n':
            teams = game.find_all('td', {'class': 'team'})
            score = game.find_all('td', {'class': 'score'})
            date = game.find_all('td', {'class': 'date'})
            table += f'{teams[0].text:^15}-{teams[1].text:^15}\n'
            table += f'{date[0].text:^15}{score[0].text:^15}\n'
            table += f'{"-" * 31}\n'
    return table


def get_promo():
    import re
    url = 'https://www.goha.ru/genshin-impact-aktualnye-promokody-na-mart-2021-goda-lWOPnm'
    headers = {'User-Agent': 'Mozilla/5.0', 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
    session = requests.Session()
    resp = session.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, 'lxml')
    codes = soup.find('strong', text=re.compile('Рабочие промокоды'))
    codes = codes.findNext('ul')
    codes = codes.find_all('strong')
    with open('genshinpromo.txt', 'r') as promofile:
        known_codes = promofile.readlines()
        known_codes = [code.rstrip() for code in known_codes]
    codes_for_sent = []
    for code in codes:
        if code.text.strip() not in known_codes:
            codes_for_sent.append(code.text.strip())
    text = '\n'.join(codes_for_sent)
    with open('genshinpromo.txt', 'a') as promofile:
        for code in codes_for_sent:
            promofile.write(code + '\n')
    return text


if __name__ == '__main__':
    print(get_football('champ', 'A'))
    # print(get_football('euro'))
    # print(get_promo())
