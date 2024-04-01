import time

import pandas as pd
from selenium import webdriver as wd
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

URL = "https://goldapple.ru/uhod"
CSV_PATH = "products.csv"

opts = wd.FirefoxOptions()
opts.add_argument("--width=1200")
opts.add_argument("--height=720")
opts.add_argument("--headless")

# ====================================================================================

def main() -> None:
    """Основная функция, которая выполняет сбор данных о продуктах, их обработку и сохранение в CSV-файл."""

    firefox_driver = wd.Firefox(options=opts)

    print("Загрузка данных...")

    # product_urls = ["https://goldapple.ru/26830400003-dreaming-with-ghosts",
    #                 "https://goldapple.ru/7430500002-eau-fraiche",
    #                 "https://goldapple.ru/19000225097"
    #                 ]

    print("Обработка данных...")

    for page in range(1, 1921):
        product_urls: list = []

        make_selenium_get_request(URL, firefox_driver, page)
        tablet_items_class = get_items_class(firefox_driver)
        product_urls = get_items_urls_on_page(tablet_items_class)
        print(f"Страница {page} обработана.")
        time.sleep(2)

        items_list: list[dict] = []
        item_number = 0
        for _url in product_urls:
            make_selenium_get_request(_url, firefox_driver)

            time.sleep(1.5)

            item_number: int = item_number + 1
            item_name: str = get_item_name(driver=firefox_driver)
            item_image: str = get_item_image(driver=firefox_driver)
            item_price: str = get_item_price(driver=firefox_driver)
            item_rating: float | str = get_item_rating(driver=firefox_driver)
            item_description: str = get_item_description(driver=firefox_driver)
            item_instructions, item_country, item_composition = manipulate_menu(driver=firefox_driver)

            items_list.append({
                "number": item_number,
                "link": _url,
                "name": item_name,
                "image": item_image,
                "price": item_price,
                "rating": item_rating,
                "description": item_description,
                "composition": item_composition,
                "instructions": item_instructions,
                "country": item_country
            })

            print("Товар {} создан!".format(item_name))

        print("Все товары были созданы. Процесс сохранения...")
        items_dataframe = get_dataframe(items_list)

        with open(CSV_PATH, 'a') as f:
            items_dataframe.to_csv(f, header = (page == 1))

        print("Все товары сохранены в {}".format(CSV_PATH))

    firefox_driver.close()


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


def get_items_class(driver):
    children = driver.find_elements(By.CLASS_NAME, "MHHxW")
    print(f"Это внутри: {children}")
    return children


def get_items_urls_on_page(tablet_items_class_content) -> list:
    product_urls: list = []
    for item in tablet_items_class_content:
        try:
            url = item.find_element(By.TAG_NAME, r'article').find_element(By.TAG_NAME, r'a')
            product_urls.append(url.get_attribute("href"))
        except NoSuchElementException:
            continue
    return product_urls


def get_all_products_urls(driver, start_page: int = 1, end_page: int = 1) -> list:
    """Функция получает список URL-адресов продуктов с веб-страницы магазина."""
    product_urls: list = []
    for page in range(start_page, end_page + 1):
        make_selenium_get_request(URL, driver, page)
        tablet_items_class = get_items_class(driver)
        product_urls += get_items_urls_on_page(tablet_items_class)
        print(f"Страница {page} обработана.")
        time.sleep(2)
    return product_urls


# ====================================================================================

def get_item_name(driver: wd):
    """Функция осуществляет поиск поле <Название> и парсит соответствующее полю значение."""
    try:
        p_item_name = driver.find_element(
            By.XPATH, '//*[@id="__layout"]/div/main/article/div[4]/div[2]/div/div[2]/div[1]/div/div/div/div[1]')
        return p_item_name.text.strip()
    except:
        return "Not available"


def get_item_price(driver: wd):
    """Функция осуществляет поиск поле <Цена> и парсит соответствующее полю значение."""
    try:
        p_item_price = driver.find_element(
            By.XPATH, '//*[@id="__layout"]/div/main/article/div[1]/div[1]/form/div[2]/div[1]/div[1]/div[1]')
        price = p_item_price.text.strip()
        return price
    except:
        return "Not available"


def get_item_image(driver: wd):
    """Функция осуществляет поиск поле <Цена> и парсит соответствующее полю значение."""
    try:
        p_item_image = driver.find_element(
            By.XPATH, '//*[@id="__layout"]/div/main/article/div[1]/div[2]/div[2]/div[1]/div/div/div/div[1]/picture/source[1]')
        image = p_item_image.get_attribute("srcset")
        return image
    except:
        return "Not available"


def get_item_description(driver: wd):
    """Функция осуществляет поиск поле <Описание> и парсит соответствующее полю значение."""
    try:
        p_item_description = driver.find_element(
            By.CLASS_NAME, r'IBqyX')
        return p_item_description.text.replace("\n", "").strip()
    except:
        return "Not available"


def get_item_rating(driver: wd) -> float | str:
    """Функция осуществляет поиск поле <Рейтинг> и парсит соответствующее полю значение."""
    try:
        p_item_rating = driver.find_element(
            By.XPATH,
            r'//*[@id="__layout"]/div/main/div[1]/div/div[3]/a[1]/div/div[1]')
        return float(p_item_rating.text.strip())
    except:
        return "Not available"


def manipulate_menu(driver: wd):
    """Функция осуществляет поиск полей <О бренде> и <Применение> и парсит соответствующее полю значение."""
    p_item_instructions = "Not available"
    p_item_country = "Not available"
    p_item_composition = "Not available"

    for i in range(1, 5):
        try:
            driver.find_element(
                By.XPATH,
                f'//*[@id="__layout"]/div/main/article/div[4]/div[2]/div/div[1]/div[1]/div/button[{i}]').click()
            menu_item = driver.find_element(
                By.XPATH, f'//*[@id="__layout"]/div/main/article/div[4]/div[2]/div/div[1]/div[1]/div/button[{i}]/div')

            if menu_item.text.strip() == "ПРИМЕНЕНИЕ":
                p_item_instructions = driver.find_element(
                    By.CLASS_NAME, r'IBqyX').text.replace("\n", "").strip()
            elif menu_item.text.strip() == "СОСТАВ":
                p_item_composition = driver.find_element(
                    By.CLASS_NAME, r'IBqyX').text.strip()
            elif menu_item.text.strip() == "О БРЕНДЕ":
                p_item_country = driver.find_element(
                    By.CLASS_NAME, r'bFC3b').text.strip()

        except NoSuchElementException:
            continue
        except:
            continue

    return p_item_instructions, p_item_country, p_item_composition


def create_item_dict(
        number: int, link: str, name: str, price: float = 0, rating: float | str = 0, description: str = "", composition: str = "",
        instructions: str = "", country: str = ""
) -> dict[str, str | float]:
    """Функция создает словарь, представляющий отдельный товар с указанными характеристиками."""
    return {
        "number": number,
        "link": link,
        "name": name,
        "price": price,
        "rating": rating,
        "description": description,
        "instructions": instructions,
        "country": country
    }


def get_dataframe(items_dict: list[dict]) -> pd.DataFrame:
    """Функция преобразует список словарей в объект DataFrame библиотеки Pandas."""
    dataframe: pd.DataFrame = pd.DataFrame(items_dict)
    return dataframe


def save_to_csv(df: pd.DataFrame, path: str | None = "products.csv") -> None:
    """Сохранение в CSV-файл."""
    df.to_csv(path, index=False, encoding="utf-8")


if __name__ == '__main__':
    main()
