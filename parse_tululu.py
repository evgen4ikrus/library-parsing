import argparse
import os
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def download_txt(url, filename, books_path):
    filepath = os.path.join(books_path, f'{sanitize_filename(filename)}.txt')
    response = requests.get(url)
    response.raise_for_status()
    with open(filepath, 'w', encoding="utf-16") as file:
        file.write(response.text)


def download_image(url, image_name, covers_pach):
    response = requests.get(url)
    response.raise_for_status()
    filepath = os.path.join(covers_pach, f'{sanitize_filename(image_name)}.jpg')
    with open(filepath, 'wb') as file:
        file.write(response.content)


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError(
            'Ответ пришёл с главной, а не с запрошенной страницы'
        )


def parse_book_page(url, html_content, book_id):
    
    soup = BeautifulSoup(html_content, 'lxml')
    book_cover_relative_link = soup.find('div',
                                         class_='bookimage').find('img')['src']
    book_cover_link = urljoin(url, book_cover_relative_link)

    book_title, book_author = soup.find('h1').text.split('::')
    book_full_title = f'{book_id}. {book_title.strip()}'

    comments_tag = soup.find_all('div', class_='texts')
    book_comments = [book_comment.find('span').text for book_comment in comments_tag]

    genres_tag = soup.find('span', class_='d_book').find_all('a')
    book_genres = [book_genre.text for book_genre in genres_tag]

    book = {
        'title': book_full_title,
        'author': book_author.strip(),
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
    start_id, end_id = get_args()

    for book_id in range(start_id, end_id + 1):
        book_download_link = f'https://tululu.org/txt.php?id={book_id}'
        response = requests.get(book_download_link)
        response.raise_for_status()

        try:
            check_for_redirect(response)
        except requests.HTTPError:
            continue

        book_link = f'https://tululu.org/b{book_id}/'
        response = requests.get(book_link)
        response.raise_for_status()
        html_content = response.text
        book = parse_book_page(book_link, html_content, book_id)

        download_txt(book_download_link, book['title'], books_path)
        download_image(book['cover_link'], book['title'], covers_pach)


if __name__ == '__main__':
    main()
