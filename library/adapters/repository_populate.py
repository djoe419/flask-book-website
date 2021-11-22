from pathlib import Path

from library.adapters.data_importer import load_books_and_authors, load_shelves, load_users, load_reviews
from library.adapters.repository import AbstractRepository


def populate(data_path: Path, repo: AbstractRepository, database_mode: bool = False):
    # publisher, book, authors
    load_books_and_authors(data_path, repo, database_mode)
    users = load_users(data_path, repo, database_mode)
    load_shelves(data_path, repo, users, database_mode)
    load_reviews(data_path, repo, database_mode)

    # remove because inventory is not used
    # load_inventory(data_path, repo, database_mode)
