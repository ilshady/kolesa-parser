import config
import logging
import pymysql
import requests
import asyncio

from bs4 import BeautifulSoup
from aiogram import Bot,Dispatcher,executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.utils import executor
from queries import Queries
from pymysql.err import IntegrityError
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
db = Queries(con)

URL = ['https://kolesa.kz/cars/toyota/corolla/region-almatinskaya-oblast/?_sys-hasphoto=2&auto-custom=2&auto-car-transm=2345&year[from]=2010&year[to]=2013&price[from]=5%20100%20000&price[to]=5%20200%20000']

HEADERS = {'user-agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36', 'accept': '*/*'}
HOST = 'https://kolesa.kz'

#Scrapping functions:
def get_html(url, params=None):
    req = requests.get(url,headers=HEADERS,params=params)
    return req

def get_content(html):
    soup = BeautifulSoup(html,'html.parser')
    items = soup.find_all('span', class_='a-el-info-title')
    cars_list = []
    for item in items:
        cars_list.append({
            'post_id' : int(item.find('a', class_='ddl_product_link').get('data-product-id')),
            'link' : HOST + item.find('a', class_='ddl_product_link').get('href')
        })
    return cars_list 

def parse():
	cars = []
	for link in URL:
		req = get_html(link)
		if req.status_code == 200:
			for page in range(1,3):
				html = get_html(link,params={'page': page})
				cars.extend(get_content(html.text))
		else:
			print('Error')
	return cars

def non_match_elements(list_a, list_b):
	non_match = []
	#to divide list in 2 cause it has duplicates
	leng = len(list_a)/2
	list_1 = list_a[:int(leng)]
	for i in list_1:
		if i not in list_b:
			non_match.append(i)
	return non_match


#Bot
class Form(StatesGroup):
    link_input = State()  # Will be represented in storage as 'Form:link_input'
    

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

@dp.message_handler(commands=['link'])
async def get_link(message: types.Message):
	await Form.link_input.set()
	await message.answer("Pass the link")


@dp.message_handler(lambda message: "kolesa.kz/cars" in message.text, state=Form.link_input)
async def check_link(message: types.Message):
	try:
		db.send_links_to_db(message.from_user.id, message.text)
	except IntegrityError:
		await message.answer("link already exists, add another")
	else:
		html = get_html(message.text)
		parsable = get_content(html.text)
		if html.status_code == 200 and parsable != []:
			await message.answer("link ok, want to add another one?")
		else:
			await message.answer("wrong link")

@dp.message_handler(commands=['done'],state=Form.link_input)
async def set_links(message: types.Message):
	user_links = db.get_link_from_db(message.from_user.id)
	#print(user_links)
	await message.reply(user_links)


@dp.message_handler(lambda message: "kolesa.kz/cars" not in message.text, state=Form.link_input)
async def check_input(message: types.Message):
	await message.reply("Встаьте правильную ссылку")

async def scheduled(wait_for):
	while True:
		await asyncio.sleep(wait_for)
		posts = db.check_item_db()
		cars = parse()
		non_match = non_match_elements(cars, posts)
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
	
	
