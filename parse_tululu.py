import argparse
import os
from pathlib import Path
from time import sleep
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from requests.exceptions import ConnectionError, HTTPError


def download_txt(url, book_id, filename, books_path):
    params = {'id': book_id}
    response = requests.get(url, params=params)
    response.raise_for_status()
    raise_for_redirect(response.history)
    filepath = os.path.join(books_path, f'{sanitize_filename(filename)}.txt')
    with open(filepath, 'w', encoding="utf-16") as file:
        file.write(response.text)


def download_image(url, book_id, image_name, covers_pach):
    params = {'id': book_id}
    response = requests.get(url, params=params)
    response.raise_for_status()
    raise_for_redirect(response.history)
    filepath = os.path.join(
        covers_pach,
        f'{sanitize_filename(image_name)}.jpg'
    )
    with open(filepath, 'wb') as file:
        file.write(response.content)


def raise_for_redirect(request_history):
    if request_history:
        raise HTTPError


def parse_book_page(url, html_content, book_id, books_pach, covers_pach):

    soup = BeautifulSoup(html_content, 'lxml')
    book_cover_relative_link = soup.find('div',
                                         class_='bookimage').find('img')['src']
    book_cover_link = urljoin(url, book_cover_relative_link)

    book_title, book_author = soup.find('h1').text.split('::')
    book_title = book_title.strip()

    img_src = os.path.join('..' , covers_pach, f'{sanitize_filename(book_title)}.jpg').replace('\\', '/')
    book_path = os.path.join('..', books_pach, f'{sanitize_filename(book_title)}.txt').replace('\\', '/')

    comments_tag = soup.find_all('div', class_='texts')
    book_comments = [book_comment.find('span').text for book_comment in comments_tag]

    genres_tag = soup.find('span', class_='d_book').find_all('a')
    book_genres = [book_genre.text for book_genre in genres_tag]

    book = {
        'title': book_title,
        'author': book_author.strip(),
        'img_src': img_src,
        'book_path': book_path,
        'comments': book_comments,
        'genres': book_genres,
        'cover_link': book_cover_link,
    }
    return book


def get_args():
    parser = argparse.ArgumentParser(
        description='Скрипт скачивает книги с сайта "https://tululu.org/"'
    )
    parser.add_argument(
        '-s',
        '--start_id',
        help='С какого id книги начать скачивание',
        type=int,
        default=1
    )
    parser.add_argument(
        '-e',
        '--end_id',
        help='На каком id книги закончить скачивание',
        type=int,
        default=10
    )
    args = parser.parse_args()
    start_id = args.start_id
    end_id = args.end_id
    return start_id, end_id


def main():

    books_path = 'books'
    covers_pach = 'covers'
    Path(books_path).mkdir(exist_ok=True, parents=True)
    Path(covers_pach).mkdir(exist_ok=True, parents=True)
    book_id, end_id = get_args()

    while book_id <= end_id:
        success_iteration = True

        try:

            book_link = f'https://tululu.org/b{book_id}/'
            response = requests.get(book_link)
            response.raise_for_status()
            raise_for_redirect(response.history)
            html_content = response.text
            book = parse_book_page(book_link, html_content, book_id, books_path, covers_pach)

            book_download_link = f'https://tululu.org/txt.php'
            download_txt(book_download_link, book_id,
                         book['title'], books_path)
            download_image(book['cover_link'], book_id,
                           book['title'], covers_pach)

        except HTTPError:
            print(f'Книги с id={book_id} нет на сайте')
            book_id += 1
            continue

        except ConnectionError:
            print('Связь с интернетом потеряна, ожидание подключения...')
            sleep(10)
            success_iteration = False

        if success_iteration:
            book_id += 1

if __name__ == '__main__':
    main()
