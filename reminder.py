from datetime import datetime

import pytz
from telebot import TeleBot
import settings
import time

bot_token = settings.BOT_TOKEN
bot = TeleBot(bot_token)
my_id = settings.MY_ID


utc = pytz.timezone('UTC')
now = utc.localize(datetime.utcnow())
final_step_time = f'{now.minute}:{now.second}.{str(now.microsecond)[:2]}'
print(final_step_time)

print('12434')
# while True:
#     time.sleep(60)
#     bot.send_message(my_id, 'напоминалка')

