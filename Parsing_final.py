import requests
from bs4 import BeautifulSoup
import csv
import lxml
from time import sleep
import random
import fake_useragent
import asyncio
import aiohttp
ua =fake_useragent.UserAgent()





def get_data(url):
    headers ={"Accept": "*/*",
              "user_agent": ua.random}
    req = requests.get(url, headers=headers)
    str_gl = req.text



get_data('https://www.tavriav.ua/')
# Открываем файл с главной страницой
with open("pythonProject3.html", encoding= "utf-8") as file:
    src = file.read()
#   обрабатываю страницу
soup = BeautifulSoup(src, 'lxml')
# for tag in soup.find_all(True):
#     print(tag.name)
# создаём таблицу
stolbci = ["data_item_category1", "data_item_category2", "data_item_category3", "data_name",  "data_brand", "data_price",  "price_discount"]
with open("katalog.csv", "w", encoding="cp1251") as file:
    writer = csv.writer(file)
    writer.writerow(stolbci)

#обьекты соуп для разных уровней меню
menu_gl = soup.findAll("li", class_="catalog-parent__item")
menu_gl2 = soup.find_all("span", class_="top-sub-catalog-name")
menu_gl3 = soup.findAll("div", class_="megadrop")
# Выводит заголовки и ссылки 1 меню
data_ultra = []
data = []
data2 = []
data3 = []
# for menu in menu_gl:
#         try:
#             qwer = "www.tavriav.ua" + (menu.find("a").get("href"))
#         except: "///"
#         qwer= qwer.strip()
#         try:
#             item = menu.find("a").text
#         except:
#                '***'
#         item= item.strip()
#
#         data.append({item: qwer})
# # print(data)
# # Выводит заголовки суб меню
# for menu2 in menu_gl2:
#     try:
#         item2 = menu2.text
#     except:
#         '***'
#     item2 = item2.strip()
#     data2.append({item2})
# print(data2)

# выводит назване группы и ссылку на неё




for menu3 in menu_gl3:
     for linki1 in  menu3.find_all('a'):
         linki = "http://www.tavriav.ua" + (linki1.get('href'))
         item3 = linki1.text.strip()
        # print(item3, linki)
         data3.append({item3: linki})
print(data3)
#  следующая проблема в том что бы в CSV файле было следующее расположение
#  категория (Напої, тютюн
#                 под категория:  Міцні алкогольні напої
#                                                  группа:  Горілка www.tavriav.ua/catalog/164/
# если делать смещение цыклов фор то получаеться хуер буер. в категорию записываеться всё.


iteration_count = int(len(data3)) - 1
count =0
print(f"Всего итераций: {iteration_count}")
def get_data_cotegoriya(data3):
    count = 0
    for i in data3:
        count +=1

        for key, value in i.items():
            url_cotegoriya = value

            headers = {"Accept": "*/*",
                       "user_agent": ua.random}
            req_cotegoriya = requests.get(value, headers=headers)
            str_cotegoriya = req_cotegoriya.text
            soup = BeautifulSoup(str_cotegoriya, 'lxml')
            page_cotegoriya = soup.find_all("li", class_="page-item")
            data4 = []
            pages = []
            for page_cotegoriya1 in page_cotegoriya:
                page_cotegoriya11 = page_cotegoriya1.text.strip()
                data4.append(page_cotegoriya11)
                data4 = [x for x in data4 if len(x.strip())]
            if len(data4) >= 3:
                data5 = data4[-1]
                try:
                    data6 = int(data5.replace(".", " ").strip())
                except: print("Ошибка")
                for i in range(data6):
                    page = (f"{value}?page={i + 1}")
                    pages.append(page)
            else:
                pages.append(value)


            for i in pages:
                headers = {"Accept": "*/*",

               "user_agent": ua.random}
                req_cotegoriya = requests.get(i, headers=headers)
                str_cotegoriya = req_cotegoriya.text
                soup = BeautifulSoup(str_cotegoriya, 'lxml')


                catalog_products_container = soup.find_all("div", class_="catalog-products__container")

                for i in catalog_products_container:

                    for data_item_category in i.find_all("div"):
                        try:
                            data_item_category1 = data_item_category.get("data-item_category")
                            if not data_item_category1: continue

                        except:
                            print('xxxx')
                        try:
                            data_item_category2 = data_item_category.get("data-item_category2")
                        except:
                            print('xxxx')

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
                        dt = []
                        dt.append(data_item_category1)
                        dt.append(data_item_category3)
                        dt.append(data_item_category2)
                        dt.append(data_name)
                        dt.append(data_brand)
                        dt.append(data_price)
                        dt.append(price_discount)


                        ##I can’t attach this cycle to the main one, I can’t add links to the general series
                        ## (category position, price, link)
                        # product_title = soup.find_all("p", class_="product__title")
                        # for p_t in product_title:
                        #
                        #     for item_category1 in p_t.find_all('a'):
                        #         item_category = item_category1.text
                        #         link_item_category = "http://www.tavriav.ua" + (item_category1.get('href'))
                        #         # print(link_item_category)
                        #         dt.append(link_item_category)

                        with open("katalog.csv", "a", newline= '', encoding="cp1251") as file:
                            writer = csv.writer(file)
                            try:
                                writer.writerow(dt)
                            except: print('\xf1')


                        sleep(random.randrange(2, 4))
                        print(count)




get_data_cotegoriya(data3)

# with open(f"stranici_kategoriy/{key}.html", "w", encoding="utf-8") as file:
#     file.write(str_cotegoriya)





