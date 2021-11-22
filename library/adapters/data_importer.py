import csv
import datetime
import json
from pathlib import Path
from typing import Dict

from werkzeug.security import generate_password_hash

from library.adapters.jsondatareader import BooksJSONReader
from library.adapters.repository import AbstractRepository
from library.domain.model import Shelve, ReadingList, User, Review


def load_books_and_authors(data_path: Path, repo: AbstractRepository, database_mode: bool):
    authors_filename = 'book_authors_excerpt.json'
    books_filename = 'comic_books_excerpt.json'
    reader = BooksJSONReader(data_path / books_filename, data_path / authors_filename)
    reader.read_json_files()

    for publisher in reader.dataset_of_publishers:
        repo.add_publisher(publisher)

    for author in reader.dataset_of_authors:
        repo.add_author(author)

    for book in reader.dataset_of_books:
        repo.add_book(book)


def read_csv_file(filename: str, delimiter=','):
    with open(filename, encoding='utf-8-sig') as infile:
        reader = csv.reader(infile, delimiter=delimiter)

        # Read first line of the the CSV file.
        headers = next(reader)

        # Read remaining rows from the CSV file.
        for row in reader:
            # Strip any leading/trailing white space from data read.
            row = [item.strip() for item in row]
            yield row


def load_shelves(data_path: Path, repo: AbstractRepository, users: Dict[int, User], database_mode: bool):
    filename = str(data_path / "shelve.csv")
    shelve_dict = dict()
    # due to cells being json object, it cant be read with default json reading
    for data_row in read_csv_file(filename, '\t'):
        shelve_id = int(data_row[0])
        shelve_json = json.loads(data_row[1])
        shelve = users[shelve_id].shelve
        for reading_list_json in shelve_json:
            # prepare reading list info
            book_ids = reading_list_json['books']
            books = repo.get_books_by_id(book_ids)
            reading_list_type = int(reading_list_json['type'])
            # name of reading list
            name = reading_list_json['name']
            is_public = reading_list_json['is_public']

            # get list entity base on list type
            if reading_list_type == 0:
                reading_list = ReadingList(name, shelve, is_public=is_public)
                shelve.add_reading_list(reading_list)
            else:
                if reading_list_type == 3:
                    reading_list = shelve.to_read_list
                elif reading_list_type == 2:
                    reading_list = shelve.currently_reading_list
                elif reading_list_type == 1:
                    reading_list = shelve.read_list
                else:
                    raise ValueError("Corrupted Database")
                reading_list.is_public = is_public
                reading_list.name = name
            # append books to list
            for book in books:
                reading_list.add_book(book)
        shelve_dict[shelve_id] = shelve
        repo.add_shelve(shelve)
    return shelve_dict


def load_users(data_path: Path, repo: AbstractRepository, database_mode: bool):
    users = dict()
    users_filename = str(data_path / "users.csv")
    for data_row in read_csv_file(users_filename):
        book_ids = [int(id) for id in str.strip(data_row[4]).split(' ')]
        books = repo.get_books_by_id(book_ids)
        user = User(
            user_name=data_row[1],
            password=generate_password_hash(data_row[2]),
            pages_read=int(data_row[3]),
        )
        for book in books:
            user.read_a_book(book)
        repo.add_user(user)
        users[int(data_row[0])] = user
    return users


def load_reviews(data_path: Path, repo: AbstractRepository, database_mode: bool):
    reviews_filename = str(data_path / "reviews.csv")
    for data_row in read_csv_file(reviews_filename):
        review = Review(
            book=repo.get_book(int(data_row[4])),
            text=data_row[5],
            rating=int(data_row[1]),
            timestamp=datetime.datetime.fromisoformat(data_row[2])
        )
        user = repo.get_user(data_row[3])
        user.add_review(review)
        repo.add_review(review, user)

# remove because inventory is not used
# def load_inventory(data_path: Path, repo: AbstractRepository, database_mode: bool):
#     inventory_filename = str(data_path / "stockentry.csv")
#     inventory = repo.get_books_inventory()
#     for i, data_row in enumerate(read_csv_file(inventory_filename)):
#         book = repo.get_book(int(data_row[0]))
#         if book is not None:
#             inventory.add_book(
#                 book,
#                 float(data_row[2]),
#                 int(data_row[1])
#             )
#         else:
#             print("Error: book %d does not exist on entry %d" % (int(data_row[0]), i+1))
