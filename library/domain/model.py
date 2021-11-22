from datetime import datetime
from itertools import permutations
from typing import List, Dict, Optional, Union

from utils import Checks


class Reviewed:

    def __init__(self):
        self.__average_rating = 0
        self.__text_reviews_count = 0
        self.__rating_count = 0

    @property
    def text_reviews_count(self) -> int:
        return self.__text_reviews_count

    @text_reviews_count.setter
    def text_reviews_count(self, ct):
        if Checks.check_int(ct):
            self.__text_reviews_count = ct
        else:
            raise ValueError("Invalid count")

    @property
    def ratings_count(self):
        return self.__rating_count

    @ratings_count.setter
    def ratings_count(self, ct):
        if Checks.check_int(ct):
            self.__rating_count = ct
        else:
            raise ValueError("Invalid count")

    @property
    def average_rating(self):
        return self.__average_rating

    @average_rating.setter
    def average_rating(self, rating):
        if isinstance(rating, float) and 0 <= rating <= 5:
            self.__average_rating = rating
        else:
            raise ValueError("Invalid rating")


class Author(Reviewed):

    def __init__(self, author_id: int, author_full_name: str):
        super().__init__()
        if not Checks.check_int(author_id):
            raise ValueError("Invalid ID")
        if not Checks.check_str(author_full_name):
            raise ValueError("Invalid Name")

        self.__id = author_id
        self.full_name = author_full_name.strip()
        self.coauthors = []

    @property
    def unique_id(self):
        return self.__id

    def __repr__(self):
        return f'<Author {self.full_name}, author id = {self.__id}>'

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return other.__id == self.__id

    def __lt__(self, other):
        return self.__id < other.__id

    def __hash__(self):
        return hash(self.__id)

    def add_coauthor(self, coauthor: 'Author') -> None:
        """add bi-directional co-author relationship"""
        if not isinstance(coauthor, Author):
            raise ValueError("Invalid author")
        if coauthor not in self.coauthors and coauthor != self:
            self.coauthors.append(coauthor)
            # coauthor.coauthors.append(self)

    def check_if_this_author_coauthored_with(self, author: 'Author') -> bool:
        return author in self.coauthors


class Publisher:
    def __init__(self, publisher_name: str):
        self.__name = publisher_name.strip() if Checks.check_str(publisher_name) else "N/A"

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, publisher_name):
        self.__name = publisher_name.strip() if Checks.check_str(publisher_name) else "N/A"

    def __repr__(self):
        # we use access via the property here
        return f'<Publisher {self.name}>'

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return other.name == self.name

    def __lt__(self, other):
        return self.name < other.name

    def __hash__(self):
        return hash(self.__name)


class Book(Reviewed):

    def __init__(self, book_id: int, title: str):
        super().__init__()
        if isinstance(book_id, str):
            # If int conversion failed, ValueError is raised through
            book_id = int(book_id)
        if not Checks.check_int(book_id):
            raise ValueError("Invalid ID")
        if not Checks.check_str(title):
            raise ValueError("Invalid title")

        self.__id = book_id
        self.__title = title.strip()
        self.__description = ""
        self.__publisher: Optional[Publisher] = None
        self.__authors: List[Author] = []
        self.__release_year = 0
        self.__ebook = False
        self.__num_pages = 0
        self.__reviews: List[Review] = []
        self.__img_url = ""
        self.__website_url = ""

    @property
    def img_url(self) -> str:
        return self.__img_url

    @img_url.setter
    def img_url(self, img_url):
        self.__img_url = img_url.strip()

    @property
    def website_url(self) -> str:
        return self.__website_url

    @website_url.setter
    def website_url(self, website_url):
        self.__website_url = website_url.strip()

    @property
    def book_id(self):
        return self.__id

    @property
    def title(self) -> str:
        return self.__title

    @title.setter
    def title(self, title):
        if Checks.check_str(title):
            self.__description = title.strip()
        else:
            raise ValueError("Invalid title")

    @property
    def description(self) -> str:
        return self.__description

    @description.setter
    def description(self, description):
        if Checks.check_str(description):
            self.__description = description.strip()
        else:
            raise ValueError("Invalid description")

    @property
    def publisher(self) -> Publisher:
        return self.__publisher

    @publisher.setter
    def publisher(self, publisher: Publisher):
        if isinstance(publisher, Publisher):
            self.__publisher = publisher

    @property
    def authors(self):
        return self.__authors

    @authors.setter
    def authors(self, authors: List[Author]):
        if isinstance(authors, List) and len(authors) > 0:
            self.__authors = authors

    @property
    def release_year(self):
        return self.__release_year

    @release_year.setter
    def release_year(self, year):
        if Checks.check_int(year):
            self.__release_year = year
        else:
            raise ValueError("Invalid year")

    @property
    def ebook(self):
        return self.__ebook

    @ebook.setter
    def ebook(self, ebook: bool):
        if isinstance(ebook, int):
            self.__ebook = not not ebook

    @property
    def reviews(self):
        return self.__reviews

    def add_review(self, review: 'Review'):
        if not isinstance(review, Review) or review.book != self:
            raise ValueError("Invalid review")
        if review in self.__reviews:
            return
        self.__reviews.append(review)

    def __repr__(self):
        return f'<Book {self.title}, book id = {self.__id}>'

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return other.__id == self.__id

    def __lt__(self, other):
        return self.__id < other.__id

    def __hash__(self):
        return hash(self.__id)

    def add_author(self, author: Author) -> None:
        if isinstance(author, Author) and author not in self.__authors:
            for existing_author in self.authors:
                author.add_coauthor(existing_author)
            self.__authors.append(author)

    def remove_author(self, author: Author) -> None:
        if author in self.authors:
            self.__authors.remove(author)

    @property
    def num_pages(self):
        return self.__num_pages

    @num_pages.setter
    def num_pages(self, value):
        if Checks.check_int(value) and value > 0:
            self.__num_pages = value
        else:
            self.__num_pages = 0


class Review:
    def __init__(self, book: Book, text: str, rating: int, timestamp: datetime = datetime.now(), user=None):
        if not isinstance(book, Book):
            book = None
        if not Checks.check_str(text):
            text = "N/A"
        if not (Checks.check_int(rating) and 1 <= rating <= 5):
            raise ValueError("Invalid rating")

        self.__book: Optional[Book] = book
        self.__text = text.strip()
        self.__rating = rating
        self.__timestamp = timestamp
        self.__user = user

    @property
    def book(self):
        return self.__book

    @property
    def review_text(self):
        return self.__text

    @property
    def rating(self):
        return self.__rating

    @property
    def timestamp(self):
        return self.__timestamp

    @property
    def user(self):
        return self.__user

    @user.setter
    def user(self, user):
        if not isinstance(user, User):
            raise ValueError("Invalid User")
        self.__user = user

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Review):
            return False
        return self.review_text == other.review_text and self.rating == other.rating and self.book == other.book \
               and self.timestamp == other.timestamp

    def __repr__(self) -> str:
        return f'<Review: {self.__rating}, "{self.__text}" ' \
               f'@{self.__timestamp.strftime("%Y/%m/%d %H:%M:%S")} for {self.__book}>'


class StockEntry:
    def __init__(self, book: Book, price: Union[float, int], stock: int):
        """
        Creates an entry of book
        :param book: Book object
        :param price: price of book
        :param stock: number of books in stock
        """
        if not isinstance(book, Book):
            raise ValueError("Invalid book")
        if not Checks.check_int(stock):
            raise ValueError("Invalid stock number")
        if not (Checks.check_int(price) or isinstance(price, float) and price >= 0):
            raise ValueError("Invalid price")
        self.book = book
        self.price = price
        self.stock = stock


class BooksInventory:

    def __init__(self):
        self.__id_stock_table: Dict[int, StockEntry] = dict()
        self.__title_book_table: Dict[str, Book] = dict()

    def add_book(self, book: Book, price: float, nr_books_in_stock: int) -> None:
        self.__title_book_table[book.title] = book
        self.__id_stock_table[book.book_id] = StockEntry(book, price, nr_books_in_stock)

    def remove_book(self, book_id: int) -> bool:
        """
        remove a book from stock
        :param book_id: id to find
        :return: whether deletion succeeded (whether book is in stock)
        """
        if book_id in self.__id_stock_table:
            book = self.__id_stock_table[book_id].book
            del self.__title_book_table[book.title]
            del self.__id_stock_table[book_id]
            return True

    def find_book(self, book_id: int) -> Optional[Book]:
        if book_id in self.__id_stock_table:
            return self.__id_stock_table[book_id].book

    def find_price(self, book_id: int) -> Optional[float]:
        if book_id in self.__id_stock_table:
            return self.__id_stock_table[book_id].price

    def find_stock_count(self, book_id: int) -> Optional[int]:
        if book_id in self.__id_stock_table:
            return self.__id_stock_table[book_id].stock

    def search_book_by_title(self, title: str) -> Optional[Book]:
        if title in self.__title_book_table:
            return self.__title_book_table[title]

    def get_number_of_entries(self):
        return len(self.__title_book_table.keys())


class ReadingList:
    TO_READ_LIST = "To read"
    CURRENTLY_READING = "Currently reading"
    READ = "Read"
    _NEXT_ID = 1

    def __init__(self, name: str, shelve: 'Shelve', uid: int = -1, is_public: bool = False):
        if not Checks.check_str(name):
            raise ValueError("Invalid name")
        if not isinstance(shelve, Shelve):
            shelve = None
            # raise ValueError("Invalid Shelve")
        if not isinstance(is_public, bool):
            is_public = False
        if not Checks.check_int(uid):
            uid = ReadingList._NEXT_ID
            ReadingList._NEXT_ID += 1

        if uid > ReadingList._NEXT_ID:
            ReadingList._NEXT_ID = uid + 1

        self.__uid = uid
        self.__name = name
        self.__shelve = shelve
        self.__is_public = is_public
        self.__books: List[Book] = []

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        if not Checks.check_str(value):
            raise ValueError("Invalid name")
        self.__name = value

    @property
    def shelve(self):
        return self.__shelve

    @shelve.setter
    def shelve(self, shelve: 'Shelve'):
        if isinstance(shelve, Shelve):
            self.__shelve = shelve

    @property
    def is_public(self):
        return self.__is_public

    @is_public.setter
    def is_public(self, value):
        if isinstance(value, bool):
            self.__is_public = value

    @property
    def books(self):
        """get books, last in first out"""
        return list(reversed(self.__books))

    def add_book(self, book: Book):
        if isinstance(book, Book):
            if book not in self.__books:
                self.__books.append(book)

    def remove_book(self, book: Book):
        if book in self.__books:
            self.__books.remove(book)

    @property
    def uid(self):
        return self.__uid

    def __eq__(self, o: object) -> bool:
        if isinstance(o, ReadingList):
            return o.uid == self.uid
        else:
            return False

    def __lt__(self, other):
        return self.uid < other.uid

    def __repr__(self) -> str:
        return '<%s %s: is_public=%s, books=[%s]' % (
            self.__class__.name, self.__name, self.is_public.__repr__(), ', '.join([repr(book) for book in self.books]))

    def __hash__(self) -> int:
        return hash(self.uid)

    def __len__(self) -> int:
        return len(self.__books)

    def __iter__(self):
        return self.books.__iter__()


class BundledReadingList(ReadingList):
    """
    Book can be appended but will be removed from any bundled reading list if already present in there.
    """

    def __init__(self, name: str, shelve: 'Shelve', uid: int = -1, is_public: bool = False):
        super().__init__(name, shelve, uid, is_public)
        self.__bundled_reading_lists: List[BundledReadingList] = []

    def bundle(self, reading_list: 'BundledReadingList'):
        self.__bundled_reading_lists.append(reading_list)

    def is_bundled_with(self, reading_list: 'BundledReadingList'):
        return reading_list in self.__bundled_reading_lists

    def add_book(self, book: Book):
        for reading_list in self.__bundled_reading_lists:
            if book in reading_list:
                reading_list.remove_book(book)
        super().add_book(book)

    def __repr__(self):
        return super().__repr__()


class ReadReadingList(BundledReadingList):
    def add_book(self, book: Book):
        if isinstance(book, Book):
            if self.shelve.user is not None:
                self.shelve.user.read_a_book(book)
            super(BundledReadingList, self).add_book(book)

    def __repr__(self):
        return super().__repr__()


class Shelve:
    def __init__(self, user: 'User' = None):
        self.__reading_lists: List[ReadingList] = []

        self.__to_read: BundledReadingList = None
        self.__currently_reading: BundledReadingList = None
        self.__read: BundledReadingList = None

        self.__user = user

    def post_init(self):
        self.__to_read = BundledReadingList(ReadingList.TO_READ_LIST, self)
        self.__currently_reading = BundledReadingList(ReadingList.CURRENTLY_READING, self)
        self.__read = ReadReadingList(ReadingList.READ, self)
        # bundle them together
        for a, b in permutations((self.__to_read, self.__currently_reading, self.__read), 2):
            a.bundle(b)
        # add to lists
        for reading_list in (self.__to_read, self.__currently_reading, self.__read):
            self.reading_lists.append(reading_list)

    @property
    def user(self):
        return self.__user

    @user.setter
    def user(self, value):
        self.__user = value

    @property
    def reading_lists(self):
        return self.__reading_lists

    @property
    def to_read_list(self):
        return self.__to_read

    @property
    def currently_reading_list(self):
        return self.__currently_reading

    @property
    def read_list(self):
        return self.__read

    def add_reading_list(self, reading_list: ReadingList) -> bool:
        """

        :param reading_list: to add
        :return: whether succeed
        """
        if not isinstance(reading_list, ReadingList):
            return False
        if reading_list in self.__reading_lists:
            return False

        self.__reading_lists.append(reading_list)
        reading_list.shelve = self

    def remove_reading_list(self, reading_list: ReadingList):
        if reading_list in self.__reading_lists and reading_list not in (
        self.__to_read, self.__currently_reading, self.__read):
            self.reading_lists.remove(reading_list)
        reading_list.shelve = None

    def __iter__(self):
        return iter(self.reading_lists)


class User:
    def __init__(self, user_name: str, password: str, pages_read=0, shelve=None):
        if not Checks.check_str(user_name):
            user_name = None
        if not isinstance(password, str) or len(password) < 7:
            password = None
        if not Checks.check_int(pages_read):
            pages_read = 0
        if not isinstance(shelve, Shelve):
            shelve = Shelve()
            shelve.post_init()
        self.__user_name: Optional[str] = None if user_name is None else user_name.strip().lower()
        self.__password: Optional[str] = password
        self.__read_books: List[Book] = []
        self.__reviews: List[Review] = []
        self.__pages_read: int = pages_read
        self.__shelve = shelve
        shelve.user = self

    @property
    def user_name(self):
        return self.__user_name

    @property
    def password(self):
        return self.__password

    @property
    def read_books(self):
        return self.__read_books

    @property
    def reviews(self):
        return self.__reviews

    @property
    def pages_read(self):
        return self.__pages_read

    def __eq__(self, o: object) -> bool:
        if isinstance(o, User):
            return self.user_name == o.user_name
        else:
            return False

    def __lt__(self, other) -> bool:
        return self.user_name < other.user_name

    def __repr__(self) -> str:
        return f'<User {self.__user_name}>'

    def __hash__(self) -> int:
        return hash(self.user_name)

    def read_a_book(self, book: Book) -> None:
        if not isinstance(book, Book):
            raise ValueError("Invalid book")
        if book in self.__read_books:
            return
        self.__read_books.append(book)
        self.__pages_read += book.num_pages if Checks.check_int(book.num_pages) else 0

    def add_review(self, review: Review) -> None:
        if not isinstance(review, Review):
            raise ValueError("Invalid review")
        if review in self.__reviews:
            return
        review.user = self
        self.__reviews.append(review)

    @property
    def shelve(self):
        return self.__shelve


def make_review(review_text: str, rating: int, user: User, book: Book, timestamp: datetime = datetime.now()):
    review = Review(book, review_text, rating, timestamp, user)
    book.add_review(review)
    user.add_review(review)
    return review
