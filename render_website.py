from jinja2 import Environment, FileSystemLoader, select_autoescape
import json
from livereload import Server
from more_itertools import chunked
import os


env = Environment(
    loader=FileSystemLoader('.'),
    autoescape=select_autoescape(['html', 'xml'])
)


def rebuild():

    template = env.get_template('template.html')
    books_per_page = 10
    
    with open("my_library/book_catalog.json", "r", encoding='utf8') as my_file:
        book_catalog_json = my_file.read()

    folder_path = 'pages'
    os.makedirs(folder_path, exist_ok=True)
    books = json.loads(book_catalog_json)
    books_on_pages  = list(chunked(books, books_per_page))

    for page_num, books_on_page in enumerate(books_on_pages, start=1):
        number_pages = len(books_on_pages)
        file_name = f'index{page_num}.html'
        file_path = os.path.join(folder_path, file_name)
        
        rendered_page = template.render(
            books_on_page=books_on_page,
            number_pages=number_pages,
            page_num=page_num,
        )

        with open(file_path, 'w', encoding="utf8") as file:
            file.write(rendered_page)


if __name__ == '__main__':

    server = Server()
    server.watch('template.html', rebuild)
    server.serve(root='.')