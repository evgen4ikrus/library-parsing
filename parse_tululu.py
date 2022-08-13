import argparse
import os
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def download_txt(url, filename, folder='books/'):
    filepath = os.path.join(f'{folder}{sanitize_filename(filename)}.txt')
    response = requests.get(url)
    response.raise_for_status()
    with open(filepath, 'w', encoding="utf-16") as file:
        file.write(response.text)


def download_image(url, image_name, folder='covers/'):
    response = requests.get(url)
    response.raise_for_status()
    filepath = os.path.join(f'{folder}{sanitize_filename(image_name)}.jpg')
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
    book_title = book_title.strip()
    book_author = book_author.strip()
    book_full_title = f'{book_id}. {book_title}'

    comments_tag = soup.find_all('div', class_='texts')
    book_comments = []
    for book_comment in comments_tag:
        book_comments.append(book_comment.find('span').text)

    genres_tag = soup.find('span', class_='d_book').find_all('a')
    book_genres = []
    for book_genre in genres_tag:
        book_genres.append(book_genre.text)

    book = {
        'title': book_full_title,
        'author': book_author,
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

    os.makedirs('books', exist_ok=True)
    os.makedirs('covers', exist_ok=True)
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

        download_txt(book_download_link, book['title'])
        download_image(book['cover_link'], book['title'])


if __name__ == '__main__':
    main()
