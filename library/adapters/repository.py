import abc
from datetime import date
from typing import List, Optional

from library.domain.model import Book, Publisher, Author, BooksInventory, User, Review, ReadingList, Shelve


class RepositoryException(Exception):
    def __init__(self, message=None):
        pass


class AbstractRepository(abc.ABC):

    @abc.abstractmethod
    def add_user(self, user: User):
        """ Adds a User to the repository. """
        raise NotImplementedError

    @abc.abstractmethod
    def get_user(self, user_name) -> Optional[User]:
        """ Returns the User named user_name from the repository.

        If there is no User with the given user_name, this method returns None.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def add_author(self, author: Author):
        raise NotImplementedError

    @abc.abstractmethod
    def get_author(self, author_id) -> Optional[Author]:
        raise NotImplementedError

    @abc.abstractmethod
    def add_book(self, book: Book):
        """ Adds an Book to the repository. """
        raise NotImplementedError

    @abc.abstractmethod
    def get_book(self, book_id: int) -> Book:
        """ Returns Book with id from the repository.

        If there is no Book with the given id, this method returns None.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_books_by_year(self, target_yr: int) -> List[Book]:
        """ Returns a list of Books that were published on target_yr.

        If there are no Books on the given tear, this method returns an empty list.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_books_after_year_inclusive(self, target_yr: int) -> List[Book]:
        """ Returns a list of Books that were published on or after target_yr.

        If there are no Books on the given condition, this method returns an empty list.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_number_of_books(self) -> int:
        """ Returns the number of Books in the repository. """
        raise NotImplementedError

    # @abc.abstractmethod
    # def get_first_book(self) -> Book:
    #     """ Returns the first Book, ordered by date, from the repository.
    # 
    #     Returns None if the repository is empty.
    #     """
    #     raise NotImplementedError
    # 
    # @abc.abstractmethod
    # def get_last_book(self) -> Book:
    #     """ Returns the last Book, ordered by date, from the repository.
    # 
    #     Returns None if the repository is empty.
    #     """
    #     raise NotImplementedError

    @abc.abstractmethod
    def get_books_by_id(self, id_list):
        """ Returns a list of Books, whose ids match those in id_list, from the repository.

        If there are no matches, this method returns an empty list.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_book_ids_for_publisher(self, publisher: Publisher):
        """ Returns a list of ids representing Books that are published by `publisher`.

        If there are Books that are published by `publisher`, this method returns an empty list.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def add_publisher(self, publisher: Publisher):
        """ Adds a Publisher to the repository. """
        raise NotImplementedError

    @abc.abstractmethod
    def get_publishers(self) -> List[Publisher]:
        """ Returns the Publishers stored in the repository. """
        raise NotImplementedError

    @abc.abstractmethod
    def add_review(self, review: Review, user: User):
        """ Adds a Review to the repository.
        It checks for if a review is in user's reviews
        The method also checks if the article in the review is in the database
        """
        if review not in user.reviews:
            raise RepositoryException
        if self.get_book(review.book.book_id) is None:
            raise RepositoryException

    @abc.abstractmethod
    def get_reviews(self):
        """ Returns the Reviews stored in the repository. """
        raise NotImplementedError

    @abc.abstractmethod
    def get_reviews_for_book(self, book: Book):
        raise NotImplementedError

    # remove because inventory is not used
    # @abc.abstractmethod
    # def get_books_inventory(self):
    #     """Returns the Book inventory"""
    #     raise NotImplementedError

    @abc.abstractmethod
    def get_book_shelves(self):
        raise NotImplementedError

    @abc.abstractmethod
    def get_book_ids_by_title(self, title) -> List[int]:
        """Return the ids of books which include title as part of their title"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_author_by_name(self, author_name: str):
        """Returns author by name"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_book_ids_by_author(self, authors: int) -> List[int]:
        """Returns book ids by author"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_book_ids_by_publisher(self, publisher: int) -> List[int]:
        """Returns book ids by publisher"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_reading_list_by_id(self, id: int) -> ReadingList:
        raise NotImplementedError

    @abc.abstractmethod
    def add_reading_list(self, reading_list: ReadingList):
        raise NotImplementedError

    @abc.abstractmethod
    def remove_reading_list(self, reading_list_id: int):
        raise NotImplementedError

    @abc.abstractmethod
    def add_shelve(self, shelve: Shelve):
        raise NotImplementedError

    @abc.abstractmethod
    def get_shelves(self):
        raise NotImplementedError

    @abc.abstractmethod
    def commit(self):
        raise NotImplementedError


repo_instance: AbstractRepository = None
