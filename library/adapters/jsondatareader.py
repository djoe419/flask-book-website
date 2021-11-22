import json
from typing import Any

from library.domain.model import *
from utils import Checks


class BooksJSONReader:

    def __init__(self, books_file_name: str, authors_file_name: str):
        self.__books_file_name = books_file_name
        self.__authors_file_name = authors_file_name

        self.__dataset_of_books = []
        self.__authors: Dict[int, Author] = dict()
        self.__publishers: Dict[str, Publisher] = dict()

    @property
    def dataset_of_books(self) -> list:
        return self.__dataset_of_books

    @property
    def dataset_of_authors(self) -> List[Author]:
        return self.__authors.values()

    @property
    def dataset_of_publishers(self):
        return self.__publishers.values()

    def __read_authors(self):
        # book authors excerpt
        self.__authors = dict()
        with open(self.__authors_file_name) as author_file:
            lines = author_file.readlines()
            author_jsons: List[Dict[str, Any]] = [json.loads(line) for line in lines]
            author_file.close()

        # debug purposed
        # print(json.dumps(author_jsons[94], sort_keys=True, indent=4))
        for author_json in author_jsons:
            author_new = Author(int(author_json['author_id']), author_json['name'])

            # optional
            author_new.average_rating = float(author_json['average_rating'])
            author_new.ratings_count = int(author_json['ratings_count'])
            author_new.text_reviews_count = int(author_json['text_reviews_count'])

            self.__authors[int(author_json['author_id'])] = author_new

    def __read_books(self):
        # comic books excerpt
        with open(self.__books_file_name) as book_file:
            lines = book_file.readlines()
            book_jsons: List[Dict[str, Any]] = [json.loads(line) for line in lines]
            book_file.close()

        # debug purposed
        # del book_jsons[8]['popular_shelves']
        # del book_jsons[8]['similar_books']
        # print()
        # print(json.dumps(book_jsons[8], indent=1))

        for book_json in book_jsons:
            book = Book(int(book_json['book_id']), book_json['title'])
            book.description = book_json['description']
            book.ebook = book_json['is_ebook'].lower() == "true"
            book.img_url = book_json['image_url']
            book.website_url = book_json['url']
            if book_json['num_pages'] != "":
                book.num_pages = int(book_json['num_pages'])
            try:
                book.release_year = int(book_json['publication_year'])
            except ValueError:
                pass

            # publisher
            publisher_name = book_json['publisher']
            if publisher_name in self.__publishers:
                book.publisher = self.__publishers[publisher_name]
            else:
                publisher = Publisher(publisher_name)
                book.publisher = publisher
                self.__publishers[publisher_name] = publisher

            # author
            for author_json in book_json['authors']:
                author_new = self.__authors[int(author_json['author_id'])]
                for author in book.authors:
                    author_new.add_coauthor(author)
                book.add_author(author_new)
            self.dataset_of_books.append(book)

            # optional
            book.ratings_count = int(book_json['ratings_count'])
            book.average_rating = float(book_json['average_rating'])
            book.text_reviews_count = int(book_json['text_reviews_count'])

    def read_json_files(self):
        try:
            self.__read_authors()
            self.__read_books()
        except IOError or FileNotFoundError:
            print("Invalid path", self.__authors_file_name, self.__books_file_name)
            pass
