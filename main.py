import requests
import os
from dotenv import load_dotenv


def download_book(book, pach, filename):
    with open(f'{pach}{filename}', 'wb') as file:
        file.write(book)


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError('Ответ пришёл с главной, а не с запрошенной страницы')


def main():

    load_dotenv()
    book_folder=os.getenv('BOOK_FOLDER', 'books/')
    os.makedirs(book_folder, exist_ok=True)

    for number in range(1, 11):
        book_download_link = f'https://tululu.org/txt.php?id={number}'
        response = requests.get(book_download_link)
        response.raise_for_status()
        filename = f'книга{number}.txt'
        try:
            check_for_redirect(response)
        except requests.HTTPError:
            continue
        book = response.content
        download_book(book, book_folder, filename)


if __name__ == '__main__':
    main()
