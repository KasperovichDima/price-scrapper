import gettext
import json
import fake_useragent
import useragent as useragent
from aiohttp import ClientTimeout
from fake_useragent import UserAgent
import asyncio
import aiohttp
import time
import platform
import requests
from bs4 import BeautifulSoup
import csv
import datetime
import lxml
if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
dt = []
ua =UserAgent(verify_ssl=False)
start_time = time.time()

def get_data(url):
        headers ={"user_agent": ua.random}
        req = requests.get(url, headers=headers)
        str_gl = req.text
        with open("pythonProject3.html", "w", encoding="utf-8") as file:
            file.write(str_gl)
get_data('https://www.tavriav.ua/')
#
# # Открываем файл с главной страницой
with open("pythonProject3.html", encoding= "utf-8") as file:
    src = file.read()
#   # обрабатываю страницу
soup = BeautifulSoup(src, 'lxml')
# for tag in soup.find_all(True):
#     print(tag.name)

# создаём таблицу

cur_time = datetime.datetime.now().strftime("%d_%m_%Y")


#обьекты соуп для разных уровней меню
menu_gl = soup.findAll("li", class_="catalog-parent__item")
menu_gl2 = soup.find_all("span", class_="top-sub-catalog-name")
menu_gl3 = soup.findAll("div", class_="megadrop")
# # Выводит заголовки и ссылки 1 меню

data = []
data2 = []

# # Выводит меню
for menu in menu_gl:
        try:
            qwer = "www.tavriav.ua" + (menu.find("a").get("href"))
        except: "///"
        qwer= qwer.strip()
        try:
            item = menu.find("a").text
        except:
               '***'
        item= item.strip()

        data.append({item: qwer})
# print(data)
# # Выводит заголовки суб меню
for menu2 in menu_gl2:
     try:
         item2 = menu2.text
     except:
         '***'
     item2 = item2.strip()
     data2.append({item2})
# print(data2)

# выводит назване группы и ссылку на неё



# включаем асинхрон

async def get_page_data(session, page):
        # print(session)
        print(page)
        headers = {"Accept": "*/*",
                   "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
                    " Chrome/104.0.0.0 Safari/537.36"}
        async with session.get(page, headers=headers) as response:
            # print(f"Страница {page}")
            response_text = await response.text()
            str_cotegoriya = response_text
            soup = BeautifulSoup(str_cotegoriya, 'lxml')
            # product_title = soup.find_all("p", class_="product__title")
            # product_prices = soup.find_all("p", class_="product__price")
            catalog_products_container = soup.find_all("div", class_="catalog-products__container")

            for i in catalog_products_container:

                print(type(i), page)
                for data_item_category in i.find_all("div"):
                    try:
                        data_item_category3 = data_item_category.get("data-item_category3")
                        if not data_item_category3: continue
                    except:  print('xxxx')
                    try:
                        data_item_category2 = data_item_category.get("data-item_category2")
                    except: print('xxxx')

                    try:
                        data_item_category1 = data_item_category.get("data-item_category")
                    except: print('xxxx')
                    data_item_category3 = data_item_category.get("data-item_category3")
                    data_brand = data_item_category.get("data-brand")
                    data_name = data_item_category.get("data-name")
                    data_price = data_item_category.get("data-price")
                    try:
                        price_discount1 = str(data_item_category.find("span", class_="price__discount")).strip()
                        clean_name = price_discount1.replace('<span class="price__discount">', " ")
                        clean_name2 = clean_name.replace("</span>", " ").strip()
                        clean_name3 = clean_name2.replace('₴', " ").strip()
                        price_discount = clean_name3
                        if not price_discount: continue
                    except:
                        print("XXXXXX")


                    dt.append({"data_item_category1": data_item_category1,
                               "data_item_category3": data_item_category3,
                               "data_item_category2": data_item_category2,
                               "data_name": data_name,
                               "data_brand":data_brand,
                               "data_price":data_price,
                               "price_discount": price_discount,
                    }

                    )
                    # print(dt)
        print(f"[INFO] Обработал страницу {page}")

async def gather_data():
    data3 = []
    url_cotegoriya =[]
    for menu3 in menu_gl3:
        for linki1 in menu3.find_all('a'):
            linki = "http://www.tavriav.ua" + (linki1.get('href'))
            item3 = linki1.text.strip()
            data3.append({item3: linki})


    iteration_count = int(len(data3)) - 1

    print(f"Всего итераций: {iteration_count}")
    for i in data3:

        for key, value in i.items():
            url_cotegoriya.append(value)

    headers = {"Accept": "*/*",
               "user_agent": ua.random}

    for url in url_cotegoriya:

        print(url)
        timeout = ClientTimeout(total=600)
        async with aiohttp.ClientSession(timeout=timeout) as session:

        # узнаём сколько страниц в категории

            req_cotegoriya = await session.get(url= url, headers=headers)
            print(url)
            soup = BeautifulSoup(await req_cotegoriya.text(), "lxml")
            page_cotegoriya = soup.find_all("li", class_="page-item")
            data4 = []

            pages = []
            tasks = []
            for page_cotegoriya1 in page_cotegoriya:
                page_cotegoriya11 = page_cotegoriya1.text.strip()
                data4.append(page_cotegoriya11)
                data4 = [x for x in data4 if len(x.strip())]
            if len(data4) >= 3:
                data5 = data4[-1]
                try:
                    data6 = int(data5.replace(".", " ").strip())
                except:
                    print("Ошибка")

                for i in range(data6):

                    page = (f"{url}?page={i + 1}")

                    pages.append(page)

            else:
                pages.append(url)

        # print(value)
        # print(pages)
            for page1 in pages:
                task = asyncio.create_task(get_page_data(session, page1))
            await asyncio.sleep(5.5)
            tasks.append(task)
        # for i in range(data6):
        #    # print(i)
        #    page = (f"{url}?page={i + 1}")
        #    # print(page)
        #    # pages.append(page)
        #    task = asyncio.create_task(get_page_data(session, page))


        # async with asyncio.Semaphore(5):
        #    await get_page_data(session, page)

           # print(f"Страница задачи {page}")

           # print(task)


            await asyncio.gather(*tasks)
            asyncio.all_tasks(loop=None)



def main():
    asyncio.run(gather_data())

    # time.sleep(1)

    stolbci = ["data_item_category1", "data_item_category2", "data_item_category3", "data_name", "data_brand",
               "data_price", "price_discount"]
    with open(f"katalog_{cur_time}.csv", "w", newline='', encoding="UTF-8") as file:
        writer = csv.writer(file)
        writer.writerow(stolbci)
    with open(f"katalog_{cur_time}_async.json", "w", encoding="UTF-8") as file:
        json.dump(dt, file, indent=4, ensure_ascii=False)


    for i in dt:
        with open(f"katalog_{cur_time}.csv", "a", newline='',  encoding="UTF-8") as file:
                  writer = csv.writer(file)
                  try:
                    writer.writerow(
                        (     i["data_item_category1"],
                              i["data_item_category3"],
                              i["data_item_category2"],
                              i["data_name"],
                              i["data_brand"],
                              i["data_price"],
                              i["price_discount"])
                                 )
                  except:
                         print('\xf1')




    finish_time = time.time() - start_time
    print(f"Затраченное на работу скрипта время: {finish_time}")

if __name__ == "__main__":

     main()
