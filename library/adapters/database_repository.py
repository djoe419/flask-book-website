from typing import List

from sqlalchemy.orm.exc import NoResultFound

from sqlalchemy.orm import scoped_session
from flask import _app_ctx_stack

from library.domain.model import User, Review, Publisher, Author, BooksInventory, ReadingList, Book, Shelve
from library.adapters.repository import AbstractRepository


class SessionContextManager:
    def __init__(self, session_factory):
        self.__session_factory = session_factory
        self.__session = scoped_session(self.__session_factory, scopefunc=_app_ctx_stack.__ident_func__)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.rollback()

    @property
    def session(self):
        return self.__session

    def commit(self):
        self.__session.commit()

    def rollback(self):
        self.__session.rollback()

    def reset_session(self):
        # this method can be used e.g. to allow Flask to start a new session for each http request,
        # via the 'before_request' callback
        self.close_current_session()
        self.__session = scoped_session(self.__session_factory, scopefunc=_app_ctx_stack.__ident_func__)

    def close_current_session(self):
        if not self.__session is None:
            self.__session.close()


class SqlAlchemyRepository(AbstractRepository):

    def commit(self):
        self._session_cm.commit()

    def __init__(self, session_factory):
        self._session_cm = SessionContextManager(session_factory)

    def close_session(self):
        self._session_cm.close_current_session()

    def reset_session(self):
        self._session_cm.reset_session()

    def like(self, str):
        return '%{}%'.format(str)

    def get_ids(self, books: List[Book]):
        return [book.book_id for book in books]

    def add_user(self, user: User):
        with self._session_cm as scm:
            scm.session.add(user)
            scm.commit()

    def get_user(self, user_name: str) -> User:
        user = None
        try:
            user = self._session_cm.session.query(User).filter(User._User__user_name == user_name).one()
        except NoResultFound:
            pass

        return user

    def add_author(self, author: Author):
        with self._session_cm as scm:
            scm.session.add(author)
            scm.commit()

    def get_author(self, author_id) -> Author:
        author = None
        try:
            author = self._session_cm.session.query(Author).filter(Author._Author__id == author_id).one()
        except NoResultFound:
            pass

        return author

    def add_book(self, book: Book):
        with self._session_cm as scm:
            scm.session.add(book)
            scm.commit()

    def get_book(self, book_id: int) -> Book:
        book = None
        try:
            book = self._session_cm.session.query(Book).filter(Book._Book__id == book_id).one()
        except NoResultFound:
            # Ignore any exception and return None.
            pass

        return book

    def get_books_by_year(self, target_yr: int) -> List[Book]:
        books_by_year = self._session_cm.session.query(Book).filter(Book._Book__release_year == target_yr).all()
        return books_by_year

    def get_books_after_year_inclusive(self, target_yr: int) -> List[Book]:
        books_after_year = self._session_cm.session.query(Book).filter(Book._Book__release_year >= target_yr).all()
        return books_after_year

    def get_number_of_books(self) -> int:
        number_of_books = self._session_cm.session.query(Book).count()
        return number_of_books

    def get_books_by_id(self, id_list) -> List[Book]:
        books_by_id = self._session_cm.session.query(Book).filter(Book._Book__id.in_(id_list)).all()
        books_by_id = list(filter(lambda x: x is not None,
                                  [next((book for book in books_by_id if book.book_id == id), None) for id in id_list]))
        return books_by_id

    def get_book_ids_by_title(self, title: str) -> List[int]:
        books_ids_by_title = self._session_cm.session.query(Book).filter(Book._Book__title.like(self.like(title))).all()
        books_ids_by_title = self.get_ids(books_ids_by_title)
        return books_ids_by_title

    def get_book_ids_by_author(self, author: int) -> List[int]:
        books = self._session_cm.session.query(Book).filter(Book._Book__authors.contains(author)).all()
        book_ids_by_author = self.get_ids(books)
        return book_ids_by_author

    def get_book_ids_for_publisher(self, publisher: Publisher) -> List[int]:
        try:
            publisher = self._session_cm.session.query(Publisher).filter(Publisher._Publisher__name == publisher.name).one()
        except NoResultFound:
            # Ignore any exception and return None.
            return []
        books = self._session_cm.session.query(Book).filter(Book._Book__publisher == publisher).all()
        book_ids_for_publisher = self.get_ids(books)
        return book_ids_for_publisher

    def add_publisher(self, publisher: Publisher):
        with self._session_cm as scm:
            scm.session.add(publisher)
            scm.commit()

    def get_publishers(self) -> List[Publisher]:
        publishers = self._session_cm.session.query(Publisher).all()
        return publishers

    def add_review(self, review: Review, user: User):
        super().add_review(review, user)
        with self._session_cm as scm:
            scm.session.add(review)
            scm.commit()

    def get_reviews(self) -> List[Review]:
        reviews = self._session_cm.session.query(Review).all()
        return reviews

    def get_reviews_for_book(self, book: Book):
        reviews_for_book = self._session_cm.session.query(Review).filter(Review._Review__book == book).all()
        return reviews_for_book

    def get_author_by_name(self, author_name: str) -> Author:
        author_by_name = None
        try:
            author_by_name = self._session_cm.session.query(Author).filter(Author.full_name == author_name).one()
        except NoResultFound:
            # Ignore any exception and return None.
            pass

        return author_by_name

    def get_book_ids_by_publisher(self, publisher: Publisher) -> List[Book]:
        return self.get_book_ids_for_publisher(publisher)

    def add_reading_list(self, reading_list: ReadingList):
        with self._session_cm as scm:
            scm.session.add(reading_list)
            scm.commit()

    def remove_reading_list(self, reading_list_id: int):
        with self._session_cm as scm:
            scm.session.query(ReadingList).filter(ReadingList._ReadlingList__uid == reading_list_id).delete()
            scm.commit()

    def add_shelve(self, shelve: Shelve):
        with self._session_cm as scm:
            scm.session.add(shelve)
            scm.commit()

    def get_shelves(self):
        shelves = self._session_cm.session.query(Shelve).all()
        return shelves

    def get_book_shelves(self):
        book_shelve = self._session_cm.session.query(Shelve).all()
        return book_shelve

    def get_reading_list_by_id(self, id_: int) -> ReadingList:
        reading_list_by_id = None
        try:
            reading_list_by_id = self._session_cm.session.query(ReadingList).filter(
                ReadingList._ReadingList__uid == id_).one()
        except NoResultFound:
            # Ignore any exception and return None.
            pass

        return reading_list_by_id
