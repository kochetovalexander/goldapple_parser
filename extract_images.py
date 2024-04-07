import time
import re

import pandas as pd
from selenium import webdriver as wd
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

URL = "https://goldapple.ru/uhod/uhod-za-licom"
CSV_PATH = "products_images.csv"

CLASS_LIST_ITEM = "MjtQ7"

opts = wd.FirefoxOptions()
opts.add_argument("--width=1200")
opts.add_argument("--height=2600")
opts.add_argument("--headless")

def main() -> None:
    """Основная функция, которая выполняет сбор данных о продуктах, их обработку и сохранение в CSV-файл."""

    firefox_driver = wd.Firefox(options=opts)

    print("Загрузка данных...")

    print("Обработка данных...")

    try:
        start_page = int(open('start_page.txt', 'r').read().strip())
    except:
        start_page = 1

    for page in range(start_page, 916):
        product_urls: list = []
        items_list: list[dict] = []

        time.sleep(2)

        print(f"Страница {page}...")

        open('start_page.txt', 'w').write(f"{page}")

        try:
            make_selenium_get_request(URL, firefox_driver, page)
            children = firefox_driver.find_elements(By.CLASS_NAME, CLASS_LIST_ITEM)
        except:
            time.sleep(5)
            exit(1)

        for item in children:
            try:
                url = item.find_element(By.TAG_NAME, r'article').find_element(By.TAG_NAME, r'a').get_attribute("href")
                images = item.find_element(By.TAG_NAME, r'picture').find_elements(By.TAG_NAME, r'source')
                for image in images:
                    src = image.get_attribute('srcset')
                    print(src)
                    match = re.search('\.jpe?g$', src)
                    if match:
                        break

                print("Choosen image:\n\t" + src)

                item_id = re.sub(r'^.+/(\d+)\D?.*$', r'\1', url)
                print(url + ' -> ' + item_id)

                items_list.append({
                    "link": url,
                    "image": src
                })

                print(items_list)

            except Exception as e:
                print(repr(e))
                print(item.get_attribute('innerHTML'))
                # exit(2)
                continue

        print("Все товары были созданы. Процесс сохранения...")
        items_dataframe = pd.DataFrame(items_list)

        with open(CSV_PATH, 'a') as f:
            items_dataframe.to_csv(f, header = (page == 1))

        print("Все товары сохранены в {}".format(CSV_PATH))


    firefox_driver.close()
    exit(0)

# ====================================================================================

def make_selenium_get_request(url: str, driver, page: int | None = None) -> None:
    """Выполняет HTTP GET-запрос к указанному URL."""
    request_url = url
    if page:
        request_url += f"?p={page}"
    try:
        driver.get(request_url)
    except:
        print()


if __name__ == '__main__':
    main()
