import json
import os

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked

env = Environment(
    loader=FileSystemLoader('.'),
    autoescape=select_autoescape(['html', 'xml'])
)


def rebuild():

    template = env.get_template('template.html')
    books_per_page = 10
    
    with open("media/book_catalog.json", "r", encoding='utf8') as my_file:
        books = json.load(my_file)

    folder_path = 'pages'
    os.makedirs(folder_path, exist_ok=True)
    books_on_pages  = list(chunked(books, books_per_page))

    for page_num, books_on_page in enumerate(books_on_pages, start=1):
        pages_number = len(books_on_pages)
        file_name = f'index{page_num}.html'
        file_path = os.path.join(folder_path, file_name)
        
        rendered_page = template.render(
            books_on_page=books_on_page,
            pages_number=pages_number,
            page_num=page_num,
        )

        with open(file_path, 'w', encoding="utf8") as file:
            file.write(rendered_page)


if __name__ == '__main__':
    rebuild()
    server = Server()
    server.watch('template.html', rebuild)
    server.serve(root='.')
