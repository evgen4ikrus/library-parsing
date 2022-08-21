import requests
from parse_tululu import get_html_content, download_txt, parse_book_page, download_image
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from requests.exceptions import HTTPError
from pathlib import Path
import json


def save_json_file(book):
    book_json = json.dumps(book)
    with open('book_catalog.json', 'w', encoding='utf8') as book_json:
        json.dump(book , book_json, ensure_ascii=False)

def main():
    
    books_path = 'books'
    covers_pach = 'covers'
    Path(books_path).mkdir(exist_ok=True, parents=True)
    Path(covers_pach).mkdir(exist_ok=True, parents=True)

    book_catalog = []

    for page in range(1, 2):

        url = f'https://tululu.org/l55/{page}'
        response = requests.get(url)
        response.raise_for_status()
        html_content = get_html_content(url)
        soup = BeautifulSoup(html_content, 'lxml')
        book_selector = 'table.d_book div.bookimage a'
        book_pages = soup.select(book_selector)
        for book_page in book_pages:

            try:
                book_relative_link = book_page['href']
                book_id = book_relative_link[2:][:-1]
                book_link = urljoin(url, book_relative_link)
                html_content = get_html_content(book_link)
                book_download_link = f'https://tululu.org/txt.php?id={book_id}'
                book = parse_book_page(book_link, html_content, book_id)
                download_txt(book_download_link, book['title'], books_path)
                download_image(book['cover_link'], book['title'], covers_pach)
                book_catalog.append(book)

            except HTTPError:
                print(f'Книги с id={book_id} нет на сайте')
                continue

    save_json_file(book_catalog)

if __name__ == '__main__':
    main()
