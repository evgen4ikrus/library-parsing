import requests
import os


def download_book(url, pach, filename):
    response = requests.get(url)
    response.raise_for_status()
    with open(f'{pach}{filename}', 'wb') as file:
        file.write(response.content)


def main():
    os.makedirs('books/', exist_ok=True)
    url = 'https://tululu.org/txt.php?id=32168'
    pach = 'books/'
    filename = 'книга.txt'
    download_book(url, pach, filename)


if __name__ == '__main__':
    main()
