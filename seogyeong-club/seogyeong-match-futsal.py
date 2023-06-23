import csv
import time
from datetime import date, datetime
from typing import List, Tuple

from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import (
    expected_conditions as EC,  # available since 2.26.0
)
from selenium.webdriver.support.ui import WebDriverWait
from urllib3.exceptions import MaxRetryError
from webdriver_manager.chrome import ChromeDriverManager

base_url: str = "https://cafe.daum.net/skfootball"

paths: List[Tuple[str, str]] = [
    ("seoul_north_weekdays", "/Uc8P"),
    ("seoul_north_weekends", "/Uc8N"),
    ("seoul_south_weekdays", "/Uc8M"),
    ("seoul_south_weekends", "/Uc8O"),
    ("gyeongi_north_weekdays", "/Uc8L"),
    ("gyeongi_north_weekends", "/Uc8K"),
    ("gyeongi_south_weekdays", "/Uc8J"),
    ("gyeongi_south_weekends", "/Uc8I"),
    ("incheon_buchoen_weekdays", "/Uc8S"),
    ("incheon_buchoen_weekends", "/Uc8R"),
    ("other_regions_weekdays", "/Uc8U"),
    ("other_regions_weekends", "/Uc8T"),
]

service = Service(executable_path=ChromeDriverManager().install())
driver: WebDriver = webdriver.Chrome(service=service)

try:
    for board_name, path in paths:
        url: str = f"{base_url}{path}"

        driver.get(url)

        driver.switch_to.frame("down")

        next_page: str = "2"

        with open("seogyeong-match-futsal.csv", "w", newline="") as f:
            csv_writer = csv.writer(f)
            while True:
                next_board: bool = False
                article_list_e: WebElement = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "article-list"))
                )
                rows: List[WebElement] = article_list_e.find_elements(By.TAG_NAME, "tr")

                data: List[List] = list()
                for row in rows:
                    board_e: WebElement = row.find_element(By.CLASS_NAME, "td_board")
                    if board_e.text in ("안내", "공지"):
                        continue

                    try:
                        title_e: WebElement = row.find_element(
                            By.CLASS_NAME, "td_title"
                        )
                        writer_e: WebElement = row.find_element(
                            By.CLASS_NAME, "td_writer"
                        )
                        date_e: WebElement = row.find_element(By.CLASS_NAME, "td_date")
                        look_e: WebElement = row.find_element(By.CLASS_NAME, "td_look")
                    except NoSuchElementException:
                        continue

                    title: str = title_e.text
                    writer: str = writer_e.text
                    date_str: str = date_e.text
                    if ":" in date_str:
                        created_at: date = date.today()
                    else:
                        created_at: date = datetime.strptime(
                            date_str, "%y.%m.%d"
                        ).date()
                    look: int = int(look_e.text)

                    print(board_name, title, writer, created_at, look)
                    data.append([board_name, title, writer, created_at, look])

                    if created_at.year == 2021:
                        next_board = True
                        break

                csv_writer.writerows(data)

                if next_board:
                    break

                page_list_e: WebElement = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "list_paging"))
                )

                pages_e: List[WebElement] = page_list_e.find_elements(By.TAG_NAME, "li")

                for page_e in pages_e:
                    if page_e.text == next_page:
                        page_e.click()
                        next_page = str(int(next_page) + 1)
                        break

                time.sleep(1)
except MaxRetryError as e:
    print(e)
driver.quit()

print("Successfully completed")
