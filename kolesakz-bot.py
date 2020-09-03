import config
import logging
import pymysql
import requests
import asyncio

from bs4 import BeautifulSoup
from aiogram import Bot,Dispatcher,executor, types
from queries import Queries
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

db = Queries(con)

URL = 'https://kolesa.kz/cars/toyota/camry/almaty/'

HEADERS = {'user-agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36', 'accept': '*/*'}

HOST = 'https://kolesa.kz'

cars = []

def get_html(url, params=None):
    req = requests.get(url,headers=HEADERS,params=params)
    return req

def get_content(html):
    soup = BeautifulSoup(html,'html.parser')
    items = soup.find_all('a', class_='ddl_product_link')
    for item in items:
        cars.append({
            'post_id' : item.get('data-product-id'),
            'link' : HOST + item.get('href')
        })
    return cars 

def parse():
    html = get_html(URL)
    if html.status_code == 200:
        cars = []
        for page in range(1, 3):
            html = get_html(URL, params={'page': page})
            #print(html.url)
            cars.extend(get_content(html.text))
            
        #print(cars)
    else:
        print('Error')



            #send_telegram(car['link'])

#echo
@dp.message_handler(commands=['subscribe'])
async def subscribe(message: types.Message):
	if(not db.subscriber_exists(message.from_user.id)):
		# если юзера нет в базе, добавляем его
		db.add_subscriber(message.from_user.id)
	else:
		# если он уже есть, то просто обновляем ему статус подписки
		db.update_subscription(message.from_user.id, 1)
	
	await message.answer("Вы успешно подписались на рассылку!\nЖдите, скоро выйдут новые объявления и вы узнаете о них первыми")

@dp.message_handler(commands=['unsubscribe'])
async def unsubscribe(message: types.Message):
	if(not db.subscriber_exists(message.from_user.id)):
		# если юзера нет в базе, добавляем его с неактивной подпиской (запоминаем)
		db.add_subscriber(message.from_user.id, 0)
		await message.answer("Вы не подписаны.")
	else:
		# если он уже есть, то просто обновляем ему статус подписки
		db.update_subscription(message.from_user.id, 0)
		await message.answer("Вы успешно отписаны от рассылки.")


async def scheduled(wait_for):
	while True:
		await asyncio.sleep(wait_for)
		parse()
		for car in cars:
			elem_exists = db.check_item_db(car['post_id'])
			if not elem_exists:
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
	dp.loop.create_task(scheduled(180))
	executor.start_polling(dp, skip_updates=True)