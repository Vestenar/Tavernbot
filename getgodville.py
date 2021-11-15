import requests
import json

translate = {'name': '<b>Имя героя: </b>',
             # 'godname': 'Имя бога: ',
             'gender': '<b>Пол: </b>',
             'level': '<b>Уровень: </b>',
             'female': 'Ж',
             'male': 'М',
             'clan': '<b>Состоит в: </b>',
             'alignment': '<b>Характер: </b>',
             'bricks_cnt': '<b>Кирпичиков уже: </b>',
             'wood_cnt': '<b>Бревнышков аж: </b>',
             'ark_f': '<b>Самочек: </b>',
             'ark_m': '<b>Самцов: </b>',
             'words': '<b>Слов для книжки: </b>',
             'pet_name': '<b>Пета зовут: </b>',
             'pet_class': '<b>Вид животинки: </b>',
             'pet_level': '<b>Уровень пета: </b>',
             'savings': '<b>Непропитых денег: </b>',
             'shop_name': '<b>Лавка: </b>',
             'savings_completed_at': '<i><b>Открытие лавки: </b></i>',
             'temple_completed_at': '<i><b>Храм отлит </b></i>',
             'ark_completed_at': '<i><b>Ковчег сколочен </b></i>',
             'book_at': '<i><b>Книжка дописана: </b></i>',
             'boss_name': '<b>Боссяра: </b>',
             'boss_power': '<b>Шириной в </b>'
             }


def transform_date(text):
    from re import findall
    data = findall(r'\d{4}-\d{2}-\d{2}', text)
    if data:
        text = '.'.join(reversed(data[0].split('-')))
    return text


def god_info(god_name):
    url = 'https://godville.net/gods/api/{}'.format(god_name)
    response = requests.get(url)
    if response.status_code != 200:
        return 'Такого не знаю, увы'
    godinfo = json.loads(response.content)
    god_name = godinfo['godname']
    info = [f'<a href="https://godville.net/gods/{god_name.replace(" ", "%20")}">{god_name}</a>']
    for key, value in godinfo.items():
        if key not in ['pet', 'inventory'] and key in translate:
            info.append(''.join([translate[key], translate[value] if value in translate else transform_date(str(value))]))

    if 'pet' in godinfo:
        for key, value in godinfo['pet'].items():
            if key not in ['pet', 'inventory'] and key in translate:
                info.append(''.join([translate[key], translate[value] if value in translate else str(value)]))
    return '\n'.join(info)


def god_prognoz():
    from bs4 import BeautifulSoup
    url = 'https://godville.net/news'
    headers = {'User-Agent': 'Mozilla/5.0', 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
    session = requests.Session()
    resp = session.get(url, headers=headers)
    session.close()
    if resp.status_code != 200:
        return 'Какой такой прогноз? Пивные ливни'
    soup = BeautifulSoup(resp.text, 'lxml')
    prognoz = soup.find_all('div', {'class': 'fc clearfix'})[0].text

    return prognoz


def check_state():
    headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
               'Accept - Encoding': 'gzip, deflate, br',
               'Accept - Language': 'ru, en - US;q = 0.7, en;q = 0.3',
               'Connection': 'keep - alive', 'DNT': '1',
               'Host': 'stats.godville.net', 'Upgrade - Insecure - Requests': '1',
               'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:86.0) Gecko/20100101 Firefox/86.0'}

    def need_registration(auth_token):
        url = 'https://godville.net/news'
        session = requests.session()
        r = session.get(url, headers=headers, cookies={'auth_token': auth_token})
        session.close()
        return 'регистрация' in str(r.content.decode('utf-8', 'replace'))

    def register():
        params = {'username': 'Nobody2',
                  'password': 'qwer12345',
                  'save_login': 'true',
                  'redirect_url': r'https://godville.net/superhero/',
                  'commit': 'Войти!'}
        url = r'https://godville.net/login/login'
        session = requests.session()
        resp = session.post(url, data=params, headers=headers)
        auth_token = resp.cookies['auth_token']
        with open('nobody.cks', 'w') as cks_file:
            cks_file.write(auth_token)
        session.close()
        return auth_token

    with open('nobody.cks', 'r') as cks_file:
        auth_token = cks_file.read()
    if auth_token == '':
        auth_token = register()
    if need_registration(auth_token):
        auth_token = register()

    return headers, auth_token


def god_guild(guildname):
    headers, auth_token = check_state()
    session = requests.session()
    url = r'https://stats.godville.net/guilds/' + guildname
    resp = session.get(url, headers=headers, cookies={'auth_token': auth_token})
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(resp.text, 'lxml')
    session.close()
    groups = soup.find_all('div', {'class': 'm_groups'})
    out_text = ''
    for motion in ['Новые медали', 'Годовщины', 'Ушли', 'Уходят', 'Пришли']:
        group1 = []
        group2 = []
        text = []
        for group in groups:
            if motion in group.text:
                group1 = group
                break

        if group1:
            for group in group1:
                if group != '\n' and motion in group.text:
                    group2 = group
                    break
        if group2:
            text = [name.contents[0].text for name in group2.findChildren('span', {'class': 'gns'})]

        if text:
            out_text += motion + ': ' + ', '.join(text) + '\n'

    return out_text if out_text else 'В гильдии все спокойно'


def list_god_guild(guildname='Завсегдатаи Старой Таверны'):
    headers, auth_token = check_state()
    session = requests.session()
    headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
               'Accept - Encoding': 'gzip, deflate, br',
               'Accept - Language': 'ru, en - US;q = 0.7, en;q = 0.3',
               'Connection': 'keep - alive', 'DNT': '1',
               'Host': 'godville.net', 'Upgrade - Insecure - Requests': '1',
               'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:86.0) Gecko/20100101 Firefox/86.0'}
    url = r'https://godville.net/stats/guild/' + guildname
    resp = session.get(url, headers=headers, cookies={'auth_token': auth_token})
    from bs4 import BeautifulSoup
    import csv
    import datetime
    import pytz
    soup = BeautifulSoup(resp.text, 'lxml')
    session.close()
    if 'Неизвестная гильдия' in soup.text:
        return None
    table = soup.find('table', {'class': 'g_tbl'})
    table_body = table.find('tbody')
    rows = table_body.find_all('tr')
    now = datetime.datetime.now(tz=pytz.timezone('Europe/Moscow'))
    date = f'{now.year}/{now.month}/{now.day} {now.hour}:{now.minute}'
    members = [['№', 'Имя', 'Уровень', 'Звание', 'актуально на: ', date]]
    for row in rows:
        line = row.findAll('td')
        npp = line[0].text
        name = line[1].text.split('\n')[0]
        level = line[4].text
        rank = line[6].text
        members.append([npp, name, level, rank])
    filename = f'список гильдии {guildname}.xls'
    with open(filename, 'w', encoding='UTF8') as file:
        writer = csv.writer(file, dialect='excel')
        writer.writerow(members[0])
        for line in members[1:]:
            writer.writerow(line)
    return filename


if __name__ == '__main__':
    import time
    # print(god_info('drony'))
    # print(god_guild('Энлайт'))
    time.sleep(2)
    # print(god_guild('4PDA'))
    # time.sleep(10)
    # print(god_guild('Завсегдатаи старой таверны'))
    # time.sleep(10)
    # print(god_guild('Орден водяной вороны'))
    # time.sleep(10)
    # print(god_guild('asylum mortuis'))
    print(list_god_guild('asylum mortuis'))
