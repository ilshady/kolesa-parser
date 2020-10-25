import requests

from bs4 import BeautifulSoup

class Parser:
    
    def __init__(self):
        self.HEADERS = {'user-agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36', 'accept': '*/*'}
        self.HOST = 'https://kolesa.kz'

    #Scrapping functions:
    def get_html(self, url, params=None):
        req = requests.get(url,headers=self.HEADERS,params=params)
        return req

    def get_content(self, html):
        soup = BeautifulSoup(html,'html.parser')
        items = soup.find_all('span', class_='a-el-info-title')
        cars_list = []
        for item in items:
            cars_list.append({
                'post_id' : int(item.find('a', class_='ddl_product_link').get('data-product-id')),
                'link' : self.HOST + item.find('a', class_='ddl_product_link').get('href')
            })
        return cars_list 

    def parse(self, urls):
        cars = []
        for link in urls:
            req = self.get_html(link)
            if req.status_code == 200:
                for page in range(1,3):
                    html = self.get_html(link,params={'page': page})
                    cars.extend(self.get_content(html.text))
            else:
                print('Error')
        return cars

    def non_match_elements(self, list_a, list_b):
        non_match = []
        #to divide list in 2 cause it has duplicates
        leng = len(list_a)/2
        list_1 = list_a[:int(leng)]
        for i in list_1:
            if i not in list_b:
                non_match.append(i)
        return non_match

