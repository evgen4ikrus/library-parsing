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
    book = {}
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'lxml')
    
    book_cover_relative_link = soup.find('div', class_='bookimage').find('img')['src']
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
        book = parse_book_page(book_link, number)
        
        download_txt(book_download_link, book['title'], folder=book_folder)
        download_image(book['cover_link'], number)


if __name__ == '__main__':
    main()
