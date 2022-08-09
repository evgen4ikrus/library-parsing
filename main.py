import requests
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin


def download_txt(url, filename, folder='books/'):
    filepath = os.path.join(f'{folder}{sanitize_filename(filename)}.txt')
    response = requests.get(url)
    response.raise_for_status()
    with open(filepath, 'wb') as file:
        file.write(response.content)


def download_image(url, number, folder='images/'):
    response = requests.get(url)
    response.raise_for_status()
    image_name = f'image_{number}'
    filepath = os.path.join(f'{folder}{sanitize_filename(image_name)}.jpg')
    with open(filepath, 'wb') as file:
        file.write(response.content)


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError('Ответ пришёл с главной, а не с запрошенной страницы')


def parse_book_page(url, book_id):
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'lxml')
    book_cover_relative_link = soup.find('div', class_='bookimage').find('img')['src']
    book_cover_link = urljoin(url, book_cover_relative_link)
    title_tag = soup.find('h1')
    book_title = title_tag.text.split('::')[0].strip()
    book_author = title_tag.text.split('::')[1].strip()
    full_book_title = f'{book_id}. {book_title}'

    return full_book_title, book_cover_link


def main():

    load_dotenv()
    book_folder=os.getenv('BOOK_FOLDER', 'books/')
    os.makedirs(book_folder, exist_ok=True)
    os.makedirs('images', exist_ok=True)

    for number in range(1, 11):
        book_download_link = f'https://tululu.org/txt.php?id={number}'
        response = requests.get(book_download_link)
        response.raise_for_status()

        try:
            check_for_redirect(response)
        except requests.HTTPError:
            continue

        book_link = f'https://tululu.org/b{number}/'
        book_title, book_cover_link = parse_book_page(book_link, number)
        
        download_txt(book_download_link, book_title, folder=book_folder)
        download_image(book_cover_link, number)


if __name__ == '__main__':
    main()
