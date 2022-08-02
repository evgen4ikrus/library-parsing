from urllib import response
import requests
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def download_txt(url, filename, folder='books/'):
    filepath = os.path.join(f'{folder}{sanitize_filename(filename)}.txt')
    response = requests.get(url)
    response.raise_for_status()
    with open(filepath, 'wb') as file:
        file.write(response.content)


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

        try:
            check_for_redirect(response)
        except requests.HTTPError:
            continue

        book_link = f'https://tululu.org/read{number}'
        response = requests.get(book_link)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'lxml')
        title_tag = soup.find('h1')
        book_title = title_tag.text.split('::')[0].strip()
        full_book_title = f'{number}. {book_title}'
        
        download_txt(book_download_link, full_book_title, folder=book_folder)


if __name__ == '__main__':
    main()
