import config
import logging
import pymysql

from aiogram import Bot,Dispatcher,executor, types
from requests import Requests
#log level
logging.basicConfig(level=logging.INFO)

#initialize
bot = Bot(token=config.API_TOKEN)
dp = Dispatcher(bot)

con = pymysql.connect(
    host='us-cdbr-east-02.cleardb.com',
    port=3306,
    user='b61694ed19c586',
    password='0a1d4b3c',
    db='heroku_7e1e49bc691f425',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

db = Requests(con)


#echo
@dp.message_handler(commands=['subscribe'])
async def subscribe(message: types.Message):
	if(not db.subscriber_exists(message.from_user.id)):
		# если юзера нет в базе, добавляем его
		db.add_subscriber(message.from_user.id)
	else:
		# если он уже есть, то просто обновляем ему статус подписки
		db.update_subscription(message.from_user.id, 1)
	
	await message.answer("Вы успешно подписались на рассылку!\nЖдите, скоро выйдут новые обзоры и вы узнаете о них первыми =)")

@dp.message_handler(commands=['unsubscribe'])
async def unsubscribe(message: types.Message):
	if(not db.subscriber_exists(message.from_user.id)):
		# если юзера нет в базе, добавляем его с неактивной подпиской (запоминаем)
		db.add_subscriber(message.from_user.id, 0)
		await message.answer("Вы итак не подписаны.")
	else:
		# если он уже есть, то просто обновляем ему статус подписки
		db.update_subscription(message.from_user.id, 0)
		await message.answer("Вы успешно отписаны от рассылки.")

# long polling

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)