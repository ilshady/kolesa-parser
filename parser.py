import requests

from bs4 import BeautifulSoup

URL = 'https://kolesa.kz/cars/toyota/camry/almaty/'

HEADERS = {'user-agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36', 'accept': '*/*'}

HOST = 'https://kolesa.kz'

def get_html(url, params=None):
    req = requests.get(url,headers=HEADERS,params=params)
    return req
'''
def get_pagecount(html):
    soup = BeautifulSoup(html,'html.parser')
    items = soup.select(".paginator ul span")
    pages = []
    for item in items:
        pages.append(
            item.text
        )
    return int(pages[-1])
'''
cars = []
'''
def send_to_db(data_id, link, title):
    cursor.execute("""INSERT INTO posts (post_id, link ) VALUES (%s,%s)""", [data_id, link])
    conn.commit()
'''

def get_content(html):
    soup = BeautifulSoup(html,'html.parser')
    items = soup.find_all('a', class_='ddl_product_link')
    for item in items:
        cars.append({
            'data_id' : item.get('data-product-id'),
            'link' : HOST + item.get('href')
        })
    return cars 

'''def check_item_db(data_id):
    sql = 'SELECT * FROM posts WHERE post_id = %s'
    cursor.execute(sql, [(int(data_id))])
    return cursor.fetchone()
'''

def parse():
    html = get_html(URL)
    if html.status_code == 200:
        cars = []
        #pages_count = get_pagecount(html.text)
        for page in range(1, 3):
            html = get_html(URL, params={'page': page})
            print(html.url)
            cars.extend(get_content(html.text))
            
        print(cars)
    else:
        print('Error')

parse()