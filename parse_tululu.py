import argparse
import os
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from pathvalidate import sanitize_filename


def download_txt(url, filename, folder='books/'):
    filepath = os.path.join(f'{folder}{sanitize_filename(filename)}.txt')
    response = requests.get(url)
    response.raise_for_status()
    with open(filepath, 'wb') as file:
        file.write(response.content)


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


def get_soup(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    return soup


def parse_book_page(url, soup, book_id):
    book = {}

    book_cover_relative_link = soup.find('div',
                                         class_='bookimage').find('img')['src']
    book['cover_link'] = urljoin(url, book_cover_relative_link)

    title_tag = soup.find('h1')
    book_title = title_tag.text.split('::')[0].strip()
    book['author'] = title_tag.text.split('::')[1].strip()
    book['title'] = f'{book_id}. {book_title}'

    comments_tag = soup.find_all('div', class_='texts')
    book_comments = []
    for book_comment in comments_tag:
        book_comments.append(book_comment.find('span').text)
    book['comments'] = book_comments

    genres_tag = soup.find('span', class_='d_book').find_all('a')
    book_genres = []
    for book_genre in genres_tag:
        book_genres.append(book_genre.text)
    book['genres'] = book_genres

    return book


def main():

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

    load_dotenv()
    os.makedirs('books', exist_ok=True)
    os.makedirs('covers', exist_ok=True)

    for book_id in range(start_id, end_id + 1):
        book_download_link = f'https://tululu.org/txt.php?id={book_id}'
        response = requests.get(book_download_link)
        response.raise_for_status()

        try:
            check_for_redirect(response)
        except requests.HTTPError:
            continue

        book_link = f'https://tululu.org/b{book_id}/'
        soup = get_soup(book_link)
        book = parse_book_page(book_link, soup, book_id)

        download_txt(book_download_link, book['title'])
        download_image(book['cover_link'], book['title'])


if __name__ == '__main__':
    main()
