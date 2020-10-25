import config
import logging
import pymysql
import requests
import asyncio

from aiogram import Bot,Dispatcher,executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.utils import executor
from pymysql.err import IntegrityError
from queries import Queries
from parser import Parser
#log level
logging.basicConfig(level=logging.INFO)

#initialize
bot = Bot(token=config.API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot,storage=storage)

#connect to db
con = pymysql.connect(
    host='us-cdbr-east-02.cleardb.com',
    port=3306,
    user='b61694ed19c586',
    password='0a1d4b3c',
    db='heroku_7e1e49bc691f425',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor,
	autocommit=True
)
urls = []
db = Queries(con)
p  = Parser()
#Bot
class Form(StatesGroup):
    link_input = State()  # Will be represented in storage as 'Form:link_input'
	default = State() # Will be represented in storage as 'Form:default'

@dp.message_handler(commands=['start'], state='*')
async def subscribe(message: types.Message):
	if(not db.subscriber_exists(message.from_user.id)):
		# если юзера нет в базе, добавляем его
		db.add_subscriber(message.from_user.id)
		await message.reply("Hello, pass the link to get notifications")
	else:
		# если он уже есть, то просто обновляем ему статус подписки
		db.update_subscription(message.from_user.id, 1)
	await Form.link_input.set()
	await message.answer("Вы успешно подписались на рассылку!\nЖдите, скоро выйдут новые объявления и вы узнаете о них первыми")

@dp.message_handler(commands=['link'], state='*')
async def get_link(message: types.Message):
	await Form.link_input.set()
	await message.answer("Pass the link")

@dp.message_handler(lambda message: "kolesa.kz/cars" in message.text, state=Form.link_input)
async def check_link(message: types.Message):
	html = p.get_html(message.text)
	parsable = p.get_content(html.text)
	if html.status_code == 200 and parsable != []:
		try:
			db.send_links_to_db(message.from_user.id, message.text)
		except IntegrityError:
			await message.answer("link already exists, add another one?")
		else:	
			await message.answer("link ok, want to add another one?")
	else:
		await message.answer("wrong link")

@dp.message_handler(commands=['done'],state=Form.link_input)
async def set_links(message: types.Message):
	user_links = db.get_link_from_db(message.from_user.id)
	global urls
	urls = user_links
	await Form.next()
	await message.reply(user_links)


@dp.message_handler(lambda message: "kolesa.kz/cars" not in message.text, state=Form.link_input)
async def check_input(message: types.Message):
	await message.reply("Вставьте правильную ссылку")

async def scheduled(wait_for):
	while True:
		await asyncio.sleep(wait_for)
		posts = db.check_item_db()
		cars = p.parse(urls)
		non_match = p.non_match_elements(cars, posts)
		for car in non_match:
			db.send_to_db(car['post_id'], car['link'])
			subscriptions = db.get_subscriptions()
				# Отправка в телеграм
			for s in subscriptions:
				await bot.send_message(
					s['user_id'],
					car['link']
					)

# long polling
if __name__ == "__main__":
	dp.loop.create_task(scheduled(10))
	executor.start_polling(dp, skip_updates=True)
	
	
