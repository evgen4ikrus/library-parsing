import argparse
import requests
from parse_tululu import get_html_content, download_txt, parse_book_page, download_image
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from requests.exceptions import HTTPError, ConnectionError
from pathlib import Path
import json
import re
from time import sleep


def save_json_file(book):
    book_json = json.dumps(book)
    with open('book_catalog.json', 'w', encoding='utf8') as book_json:
        json.dump(book , book_json, ensure_ascii=False)


def get_args():
    parser = argparse.ArgumentParser(
        description='Скрипт скачивает книги с сайта "https://tululu.org/" по жанрам'
    )
    parser.add_argument(
        '-s',
        '--start_page',
        help='С какой страницы начать скачивание книг',
        type=int,
        default=1
    )
    parser.add_argument(
        '-e',
        '--end_page',
        help='До какой страницы скачивать книги',
        type=int,
        default=float('inf')
    )
    args = parser.parse_args()
    start_page = args.start_page
    end_page = args.end_page
    return start_page, end_page


def main():
    
    books_path = 'books'
    covers_pach = 'covers'
    Path(books_path).mkdir(exist_ok=True, parents=True)
    Path(covers_pach).mkdir(exist_ok=True, parents=True)
    start_page, end_page = get_args()
    book_catalog = []

    while start_page < end_page:

        try:
            url = f'https://tululu.org/l55/{start_page}'
            response = requests.get(url)
            response.raise_for_status()
            html_content = get_html_content(url)
            soup = BeautifulSoup(html_content, 'lxml')
            book_selector = 'table.d_book div.bookimage a'
            book_pages = soup.select(book_selector)

        except HTTPError:
            print(f'Страница {start_page} не найдена')
            break

        except ConnectionError:
            print('Связь с интернетом потеряна, ожидание подключения...')
            sleep(5)
            continue

        for book_page in book_pages:
            success_iteration = False
            while success_iteration == False:

                try:
                    book_relative_link = book_page['href']
                    book_id = re.search(r'\d+', book_relative_link).group()
                    book_link = urljoin(url, book_relative_link)
                    html_content = get_html_content(book_link)
                    book_download_link = f'https://tululu.org/txt.php?id={book_id}'
                    book = parse_book_page(book_link, html_content, book_id)
                    download_txt(book_download_link, book['title'], books_path)
                    download_image(book['cover_link'], book['title'], covers_pach)
                    book_catalog.append(book)

                except HTTPError:
                    print(f'Книги с id={book_id} нет на сайте')
                    success_iteration = True

                except ConnectionError:
                    print('Связь с интернетом потеряна, ожидание подключения.')
                    sleep(5)
                    continue

                success_iteration = True

        start_page += 1

    save_json_file(book_catalog)
    print('Скачивание книг завершено')


if __name__ == '__main__':
    main()
