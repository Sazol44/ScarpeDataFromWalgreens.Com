import requests
from fake_useragent import UserAgent
import json
import pprint
from urllib.parse import urljoin
import sqlite3


ua = UserAgent()

extract_info = []


def scraper(pageNumber=1):
    url = "https://www.walgreens.com/productsearch/v1/products/search"

    payload = {"p": pageNumber, "s": 24, "view": "allView", "geoTargetEnabled": False, "abtest": [
        "tier2", "showNewCategories"], "deviceType": "desktop", "id": ["350006"], "requestType": "tier3", "source": "clPage", "sort": "Top Sellers"}
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': ua.random
    }

    response = requests.request(
        "POST", url, headers=headers, data=json.dumps(payload))

    data = response.json()

    products = data['products']

    for product_info in products:
        pro_info = product_info['productInfo']
        pr = {
            'img': urljoin(base='https://www.walgreens.com', url=pro_info['imageUrl']),
            'name': pro_info['productDisplayName'],
            'id': pro_info['prodId'],
            'price': pro_info['priceInfo']['regularPrice'],
            'size': pro_info['productSize'],
            'url': urljoin(base='https://www.walgreens.com', url=pro_info['productURL'])
        }
        extract_info.append(pr)
    pageNumber += 1
    try:
        scraper(pageNumber=pageNumber)
    except:
        return print("complete")


scraper()
connection = sqlite3.connect("walgreens.db")
c = connection.cursor()
try:
    c.execute('''
        CREATE TABLE products (
            id TEXT PRIMARY KEY,
            name TEXT,
            size TEXT,
            image TEXT,
            url TEXT,
            price TEXT
        )

    ''')
    connection.commit()
except sqlite3.OperationalError as e:
    print(e)

for product in extract_info:
    try:
        c.execute('''
                INSERT INTO products ( id, name, size, image, url, price) VALUES ( ?,?,?,?,?,? )

            ''', (
            product['id'],
            product['name'],
            product['size'],
            product['img'],
            product['url'],
            product['price']
        )
        )
    except sqlite3.IntegrityError as e:
        pass
connection.commit()
connection.close()
