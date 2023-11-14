import json
import os

import requests
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

ENDPOINT = 'https://biblias.com.br/acfonline-versos'


def get_bible_html():
    """Busca e salva os capítulos em html na pasta acf"""
    for book in range(1, 67):

        chapter = 1

        while True:

            if book <= 27:
                testament = 'nt'
            elif book > 27:
                testament = 'at'

            path = os.path.join(
                os.getcwd(),
                'acf-html',
                f'{testament}_book-{book}_chapter-{chapter}.html',
            )

            if os.path.exists(path):
                print(f'Livro: {book}, capitulo: {chapter} JÁ EXISTE!')
                chapter += 1
                continue

            url = ENDPOINT.format(book, chapter)

            params = {'livro': book, 'capitulo': chapter}

            req = requests.get(url, params=params, timeout=None)

            if len(req.text) == 0:
                break

            with open(path, 'w') as f:
                f.write(req.text)

            print(f'Livro: {book}, capitulo: {chapter} SALVO!')

            chapter += 1


def get_list_books_json():
    """Busca a lista de livros e salva em json"""
    books = {}
    driver = webdriver.Firefox()
    driver.get('https://biblias.com.br/acfonline')

    for book_num in range(1, 67):
        if book_num <= 27:
            driver.find_element(By.ID, 'btn-novo-testamento').click()
        elif book_num > 27:
            driver.find_element(By.ID, 'btn-antigo-testamento').click()
        elem = driver.find_element(By.ID, f'livro-{book_num}')
        books[book_num] = elem.text

    driver.close()

    path = os.path.join(
        os.getcwd(),
        'acf-json',
        '_books.json',
    )

    save_json(books, path, 4)


def get_bible_json():
    """Busca e salva os capítulos em json na pasta acf-json"""

    driver = webdriver.Firefox()
    driver.get('https://biblias.com.br/acfonline')

    for book in range(1, 67):

        chapter = 1

        while True:

            book_data = {}

            if book <= 27:
                testament = 'nt'
                btn = driver.find_element(By.ID, 'btn-novo-testamento')
                driver.execute_script('arguments[0].click();', btn)
            elif book > 27:
                testament = 'at'
                btn = driver.find_element(By.ID, 'btn-antigo-testamento')
                driver.execute_script('arguments[0].click();', btn)

            path = os.path.join(
                os.getcwd(),
                'acf-json',
                f'{testament}_book-{book}_chapter-{chapter}.json',
            )

            if os.path.exists(path):
                print(f'(JSON) Livro: {book}, capitulo: {chapter} JÁ EXISTE!')
                chapter += 1
                continue

            book_btn_el = driver.find_element(By.ID, f'livro-{book}')
            book_data['book'] = book
            book_data['book_name'] = book_btn_el.text
            book_data['chapter'] = chapter

            book_btn_el.click()

            try:
                driver.find_element(
                    By.ID, f'capitulo-{book}-{chapter}'
                ).click()
            except NoSuchElementException:
                break

            book_text = driver.find_element(By.ID, 'livro-texto')

            while True:
                try:
                    book_text.find_element(By.ID, 'loader')
                    continue
                except NoSuchElementException:
                    break

            book_verses = book_text.find_elements(By.CLASS_NAME, 'verse-text')

            book_data['verses'] = []

            for index, verse_el in enumerate(book_verses):
                verse = {str(index + 1): verse_el.get_attribute('innerHTML')}
                book_data['verses'].append(verse)

            if len(book_data['verses']) == 0:
                continue

            save_json(book_data, path)

            chapter += 1
    driver.close()


def save_json(data, path, indent=None):
    """Salva um dict como json

    Args:
        data (dict): Dados
        path (str): Path do arquivo
        indent (int, optional): Valor de identação do json. Defaults to None.
    """
    with open(path, 'w') as f:
        f.write(json.dumps(data, indent=indent))


if __name__ == '__main__':

    get_bible_html()
    get_list_books_json()
    get_bible_json()
