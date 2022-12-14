"""Tavria V parser."""
from typing import Generator, NamedTuple
from dotenv import load_dotenv
import asyncio
import csv
import datetime
import json
import platform
import time
from typing import Iterable

import aiohttp

import bs4

from fake_useragent import UserAgent

import requests


# if platform.system() == 'Windows':
#     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
load_dotenv()


class MenuItems(NamedTuple):
    """Different level menu items."""
    lvl_1: list
    lvl_2: list
    lvl_3: list


class TavriaParser:
    """Price parser for 'Таврія В'."""

    __menu_items: MenuItems

    def __init__(self, home_url: str) -> None:

        self.__home_url = home_url
        self.__parsed_records: list = []
        self.__user_agent = UserAgent(verify_ssl=False)

    def __call__(self) -> None:
        soup = bs4.BeautifulSoup(self.__start_page_content, 'lxml') # nuzhno?
        self.__get_menu_items(soup) # nuzhno?
        # links = self.__get_links(menu_items) # nuzhno?
        asyncio.run(self.__gather_data())

    @property
    def __start_page_content(self) -> str:
        rsp = requests.get(self.__home_url,
                           headers={"user_agent":
                           self.__user_agent.random})
        return rsp.text

    def __get_menu_items(self, soup: bs4.BeautifulSoup) -> None:
        self.__menu_items = MenuItems(
            lvl_1=soup.findAll("li", class_="catalog-parent__item"),
            lvl_2=soup.find_all("span", class_="top-sub-catalog-name"),
            lvl_3=soup.findAll("div", class_="megadrop"),
        )

    # def __get_links(self, items: MenuItems):
    #     lvl_1_links: dict[str, str] = {
    #         _.find("a").text:
    #         f'{self.__home_url}{_.find("a").get("href")}'.strip()
    #         for _ in items.lvl_1
    #     }
    #     lvl_2_names = [_.text.strip() for _ in items.lvl_2]

    async def __gather_data(self):
        """"""
        timeout = aiohttp.ClientTimeout(total=600)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            await self.__create_tasks(session)

    async def __create_tasks(self, session: aiohttp.ClientSession) -> None:
        """"""
        pages: list[str] = []
        headers = {"Accept": "*/*",
                   "user_agent": user_agent.random}

        for url in self.__lvl_3_urls:
            print(url)
            rsp = await session.get(url=url, headers=headers)
            soup = bs4.BeautifulSoup(await rsp.text(), "lxml")
            category_pages = soup.find_all("li", class_="page-item")
            data4 = [_.text.strip() for _ in category_pages if _.text.strip()]  # replace with generator
            if len(data4) >= 3:
                try:
                    data6 = int(data4[-1].replace(".", " ").strip())
                    for _ in range(data6):
                        pages.append(f'{url}?page={_ + 1}')
                except:
                    print("Ошибка")
            else:
                pages.append(url)

            tasks = [asyncio.create_task(get_page_data(session, _))
                        for _ in pages]
            # WTF?!!
            # for page1 in pages:
            #     task = asyncio.create_task(get_page_data(session, page1))
            # await asyncio.sleep(5.5)
            # tasks.append(task)
            await asyncio.gather(*tasks)
            asyncio.all_tasks(loop=None)


    @property
    def __lvl_3_urls(self) -> Generator[str, None, None]:
        """TODO: Refactoring."""
        links = (_.find_all('a') for _ in self.__menu_items.lvl_3)
        return (f'{self.__home_url}{_.get("href")}'.strip() for _ in links)










parsed_records = []  # WTF?
user_agent = UserAgent(verify_ssl=False)
START_PAGE = 'https://www.tavriav.ua/'


def get_start_page_content(url: str) -> str:
    """Get html code of start page."""
    rsp = requests.get(url, headers={"user_agent": user_agent.random})
    return rsp.text


soup = bs4.BeautifulSoup(get_start_page_content(START_PAGE), 'lxml')
# обьекты соуп для разных уровней меню
menu_items_lvl_1 = soup.findAll("li", class_="catalog-parent__item")
menu_items_lvl_2 = soup.find_all("span", class_="top-sub-catalog-name")
menu_items_lvl_3 = soup.findAll("div", class_="megadrop")

lvl_1_links: list[dict[str, str]] = []
# # Выводит меню
for menu_item in menu_items_lvl_1:
    # try:
    item_link: str = "www.tavriav.ua" + (menu_item.find("a").get("href"))
    # except:
    #     "///"
    # try:
    item_name: str = menu_item.find("a").text
    # except:
    #     '***'
    lvl_1_links.append({item_name.strip(): item_link.strip()})
# print(data)
# # Выводит заголовки суб меню

lvl_2_names = []
for menu_item in menu_items_lvl_2:
    try:
        item_name = menu_item.text.strip()
    except:
        '***'
    lvl_2_names.append({item_name})
# выводит назване группы и ссылку на неё


# включаем асинхрон
async def get_page_data(session, page):
    print(page)
    headers = {"Accept": "*/*",
               "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)\
                AppleWebKit/537.36 (KHTML, like Gecko)"
               "Chrome/104.0.0.0 Safari/537.36"}
    async with session.get(page, headers=headers) as response:
        str_cotegoriya: str = await response.text()
        soup = bs4.BeautifulSoup(str_cotegoriya, 'lxml')
        catalog_products_container = soup.find_all(
            "div", class_="catalog-products__container"
        )

        for i in catalog_products_container:

            print(type(i), page)
            for data_item_category in i.find_all("div"):
                try:
                    data_item_category3\
                        = data_item_category.get("data-item_category3")
                    if not data_item_category3:
                        continue
                except:
                    print('xxxx')
                try:
                    data_item_category2\
                        = data_item_category.get("data-item_category2")
                except:
                    print('xxxx')

                try:
                    data_item_category1\
                        = data_item_category.get("data-item_category")
                except:
                    print('xxxx')
                data_item_category3\
                    = data_item_category.get("data-item_category3")
                data_brand = data_item_category.get("data-brand")
                data_name = data_item_category.get("data-name")
                data_price = data_item_category.get("data-price")
                try:
                    price_discount1 = str(data_item_category.find(
                        "span", class_="price__discount"
                        )
                    ).strip()
                    clean_name = price_discount1.replace(
                        '<span class="price__discount">', " "
                    )
                    clean_name2 = clean_name.replace("</span>", " ").strip()
                    clean_name3 = clean_name2.replace('₴', " ").strip()
                    price_discount = clean_name3
                    if not price_discount:
                        continue
                except:
                    print("XXXXXX")

                parsed_records.append(
                    {"data_item_category1": data_item_category1,
                     "data_item_category3": data_item_category3,
                     "data_item_category2": data_item_category2,
                     "data_name": data_name,
                     "data_brand": data_brand,
                     "data_price": data_price,
                     "price_discount": price_discount,
                     }
                )
                # print(dt)
        print(f"[INFO] Обработал страницу {page}")


async def gather_data():
    lvl_3_links: list[dict[str, str]] = []
    # url_cotegoriya = []
    # menu_items_lvl_3: Iterable[bs4.element.Tag]
    for menu_item in menu_items_lvl_3:
        for link in menu_item.find_all('a'):
            link_url: str = "http://www.tavriav.ua" + (link.get('href'))
            item_name: str = link.text.strip()
            lvl_3_links.append({item_name: link_url})

    print(f"Total iterations: {len(lvl_3_links) - 1}")

    # for i in lvl_3_links:

    #     for key, value in i.items():
    #         url_cotegoriya.append(value)

    headers = {"Accept": "*/*",
               "user_agent": user_agent.random}

    for url in (tuple(_.values())[0] for _ in lvl_3_links):

        print(url)
        timeout = aiohttp.ClientTimeout(total=600)
        async with aiohttp.ClientSession(timeout=timeout) as session:

            # узнаём сколько страниц в категории

            category_response = await session.get(url=url, headers=headers)
            soup = bs4.BeautifulSoup(await category_response.text(), "lxml")
            category_pages = soup.find_all("li", class_="page-item")

            data4 = []
            pages = []
            tasks = []

            for page in category_pages:
                data4.append(page.text.strip())
                data4 = [_ for _ in data4 if len(_.strip())]
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

            for page1 in pages:
                task = asyncio.create_task(get_page_data(session, page1))
            await asyncio.sleep(5.5)
            tasks.append(task)

            await asyncio.gather(*tasks)
            asyncio.all_tasks(loop=None)


def main():
    asyncio.run(gather_data())

    # cur_time = datetime.datetime.now().strftime("%d_%m_%Y")

    # stolbci = ("data_item_category1 data_item_category2\
    #            data_item_category3 data_name data_brand\
    #            data_price price_discount").split()
    # with open(f"katalog_{cur_time}.csv", "w",
    #           newline='', encoding="UTF-8") as file:
    #     csv.writer(file).writerow(stolbci)
    # with open(f"katalog_{cur_time}_async.json", "w", encoding="UTF-8") as file:
    #     json.dump(parsed_records, file, indent=4, ensure_ascii=False)

    # for i in parsed_records:
    #     with open(f"katalog_{cur_time}.csv", "a",
    #               newline='', encoding="UTF-8") as file:
    #         try:
    #             csv.writer(file).writerow(
    #                 (i["data_item_category1"],
    #                  i["data_item_category3"],
    #                  i["data_item_category2"],
    #                  i["data_name"],
    #                  i["data_brand"],
    #                  i["data_price"],
    #                  i["price_discount"])
    #                  )
    #         except:
    #             print('\xf1')

    print(f"Затраченное на работу скрипта время: {time.time() - start_time}")


if __name__ == "__main__":
    main()
