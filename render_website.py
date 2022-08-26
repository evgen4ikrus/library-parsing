from http.server import HTTPServer, SimpleHTTPRequestHandler

from jinja2 import Environment, FileSystemLoader, select_autoescape
import json
from livereload import Server


env = Environment(
    loader=FileSystemLoader('.'),
    autoescape=select_autoescape(['html', 'xml'])
)


def rebuild():
    
    template = env.get_template('template.html')
    with open("my_library/book_catalog.json", "r", encoding='utf8') as my_file:
        book_catalog_json = my_file.read()
        
    book_catalog = json.loads(book_catalog_json)
    rendered_page = template.render(book_catalog=book_catalog)

    with open('index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)


if __name__ == '__main__':
    
    server = Server()
    server.watch('template.html', rebuild)
    server.serve(root='.')