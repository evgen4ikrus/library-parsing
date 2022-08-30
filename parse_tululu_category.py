import argparse
import json
import os
import re
from pathlib import Path
from time import sleep
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from requests.exceptions import ConnectionError, HTTPError

from parse_tululu import (download_image, download_txt,
                          parse_book_page, raise_for_redirect)


def save_json_file(book, json_path):
    book_json = json.dumps(book)
    full_json_path = os.path.join(json_path, 'book_catalog.json')
    with open(full_json_path, 'w', encoding='utf8') as book_json:
        json.dump(book, book_json, ensure_ascii=False)


def get_args():
    parser = argparse.ArgumentParser(
        description='Скрипт скачивает книги с сайта "https://tululu.org/" по категориям'
    )
    parser.add_argument(
        '-c',
        '--category_id',
        help='Указать ID категории книг',
        type=int,
        default=55
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
    parser.add_argument(
        '-а',
        '--dest_folder',
        help='Путь к каталогу с результатами парсинга: картинкам, книгам, JSON',
        default='media'
    )
    parser.add_argument(
        '-j',
        '--json_path',
        help='Указать свой путь к *.json файлу с результатами',
        default=''
    )
    parser.add_argument(
        '-si',
        '--skip_imgs',
        action='store_true',
        help='Не скачивать картинки'
    )
    parser.add_argument(
        '-st',
        '--skip_txt',
        action='store_true',
        help='Не скачивать книги'
    )
    args = parser.parse_args()
    return args


def get_json_path(args):
    if args.json_path:
        json_path = os.path.join(args.json_path)
        return json_path
    return args.dest_folder


def create_paths(*args):
    for path in args:
        Path(path).mkdir(exist_ok=True, parents=True)


def main():

    args = get_args()
    dest_folder = args.dest_folder
    books_path = os.path.join(dest_folder, 'books')
    covers_path = os.path.join(dest_folder, 'covers')
    json_path = get_json_path(args)
    create_paths(books_path, covers_path, json_path)
    start_page, end_page = args.start_page, args.end_page
    category_id = args.category_id
    book_catalog = []

    while start_page < end_page:

        try:
            url = f'https://tululu.org/l{category_id}/{start_page}'
            response = requests.get(url)
            response.raise_for_status()
            raise_for_redirect(response.history)
            html_content = response.text
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

            while not success_iteration:

                try:
                    book_relative_link = book_page['href']
                    book_link = urljoin(url, book_relative_link)
                    response = requests.get(book_link)
                    response.raise_for_status()
                    raise_for_redirect(response.history)
                    html_content = response.text

                    book_id = re.search(r'\d+', book_relative_link).group()
                    book_download_link = f'https://tululu.org/txt.php'
                    book = parse_book_page(book_link, html_content, book_id, books_path, covers_path)
                    if not args.skip_txt:
                        download_txt(book_download_link, book_id,
                                     book['title'], books_path)
                    if not args.skip_imgs:
                        download_image(book['cover_link'], book_id,
                                       book['title'], covers_path)
                    book_catalog.append(book)

                except HTTPError:
                    print(f'Книги с id={book_id} нет на сайте')
                    success_iteration = True

                except ConnectionError:
                    print('Связь с интернетом потеряна, ожидание подключения...')
                    sleep(5)
                    continue

                success_iteration = True

        start_page += 1

    save_json_file(book_catalog, json_path)
    print('Скачивание книг завершено')


if __name__ == '__main__':
    main()
