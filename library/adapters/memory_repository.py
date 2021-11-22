from typing import List, Dict
from library.domain.model import Book, Shelve
from library.adapters.repository import AbstractRepository
from library.domain.model import User, Review, Publisher, Author, BooksInventory, ReadingList


class MemoryRepository(AbstractRepository):

    def commit(self):
        pass

    def __init__(self):
        self.__authors: List[Author] = []
        self.__users: List[User] = []
        self.__books: List[Book] = []
        self.__publishers: List[Publisher] = []
        self.__reviews: List[Review] = []
        # self.__book_inventory: BooksInventory = BooksInventory()
        self.__book_index: Dict[int, Book] = {}
        self.__shelves: List[Shelve] = []
        self.__reading_lists: Dict[int, ReadingList] = {}

    def add_user(self, user: User):
        self.__users.append(user)

    def get_user(self, user_name) -> User:
        return next((user for user in self.__users if user.user_name == user_name.lower()), None)

    def add_author(self, author: Author):
        self.__authors.append(author)

    def get_author(self, author_id) -> Author:
        return next((author for author in self.__authors if author.unique_id == author_id), None)

    def add_book(self, book: Book):
        self.__books.append(book)
        self.__book_index[book.book_id] = book

    def get_book(self, book_id: int) -> Book:
        return self.__book_index[book_id] if book_id in self.__book_index else None

    def get_books_by_year(self, target_yr: int) -> List[Book]:
        return [book for book in self.__books if book.release_year == target_yr]

    def get_books_after_year_inclusive(self, target_yr: int) -> List[Book]:
        return [book for book in self.__books if book.release_year >= target_yr]

    def get_number_of_books(self) -> int:
        return self.__books.__len__()

    def get_books_by_id(self, id_list) -> List[Book]:
        return list(filter(lambda x: x is not None, map(self.get_book, id_list)))

    def get_book_ids_by_title(self, title: str) -> List[int]:
        title = title.lower()
        return [book.book_id for book in self.__books if title in book.title.lower()]

    def get_book_ids_for_publisher(self, publisher: Publisher) -> List[int]:
        return [book.book_id for book in self.__books if book.publisher == publisher]

    def add_publisher(self, publisher: Publisher):
        self.__publishers.append(publisher)

    def get_publishers(self) -> List[Publisher]:
        return self.__publishers

    def add_review(self, review: Review, user: User):
        super(MemoryRepository, self).add_review(review, user)
        self.__reviews.append(review)

    def get_reviews(self) -> List[Review]:
        return self.__reviews

    def get_reviews_for_book(self, book: Book):
        return [review for review in self.__reviews if review.book == book]

    # remove because inventory is not used
    # def get_books_inventory(self) -> BooksInventory:
    #     return self.__book_inventory

    def get_author_by_name(self, author_name: str) -> Author:
        return next((author for author in self.__authors if author.full_name == author_name), None)

    def get_book_ids_by_author(self, author: Author) -> List[Book]:
        return [book.book_id for book in self.__books if author in book.authors]

    def get_book_ids_by_publisher(self, publisher: Publisher) -> List[Book]:
        return self.get_book_ids_for_publisher(publisher)

    def add_reading_list(self, reading_list: ReadingList):
        if reading_list.uid not in self.__reading_lists:
            self.__reading_lists[reading_list.uid] = reading_list

    def remove_reading_list(self, reading_list_id: int):
        if reading_list_id in self.__reading_lists:
            del self.__reading_lists[reading_list_id]

    def add_shelve(self,shelve: Shelve):
        self.__shelves.append(shelve)
        for list_ in shelve:
            self.add_reading_list(list_)

    def get_shelves(self):
        return self.__shelves

    def get_book_shelves(self):
        return self.__shelves

    def get_reading_list_by_id(self, id_: int) -> ReadingList:
        return self.__reading_lists[id_] if id_ in self.__reading_lists else None


