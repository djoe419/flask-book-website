from datetime import date, datetime
import pytest

import library.adapters.repository as repo
from library.adapters.database_repository import SqlAlchemyRepository
from library.domain.model import User, Author, Publisher, Book, Review
from library.adapters.repository import RepositoryException


def test_repository_can_add_a_user(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    user = User('dave', '123456789')
    assert repo.get_user('dave') is None
    repo.add_user(user)

    assert repo.get_user('dave') is user

#needs fixing
def test_repository_can_retrieve_a_user(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    user = repo.get_user("ftinson0")
    assert user == User('ftinson0','3XE1blo')
    assert user.pages_read >=612
    assert len(user.read_books) >=3
    assert user.read_books[0].book_id == 13340336


def test_repository_does_not_retrieve_a_non_existent_user(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    user = repo.get_user('prince')

    assert user is None


def test_repository_can_add_a_author(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    author = Author(123, 'dave')
    assert repo.get_author(123) is None
    repo.add_author(author)

    assert repo.get_author(123) is author


def test_repository_can_retrieve_a_author(session_factory):
    repo = SqlAlchemyRepository(session_factory)
    author = repo.get_author(6384773)

    assert author == Author(6384773, 'Asma')


def test_repository_does_not_retrieve_a_non_existent_author(session_factory):
    repo = SqlAlchemyRepository(session_factory)
    author = repo.get_author(1)
    assert author is None


def test_repository_can_add_a_publisher(session_factory):
    repo = SqlAlchemyRepository(session_factory)
    publisher = Publisher('publisher_name')
    assert publisher not in repo.get_publishers()
    repo.add_publisher(publisher)

    assert publisher in repo.get_publishers()


def test_repository_can_retrieve_publishers(session_factory):
    repo = SqlAlchemyRepository(session_factory)
    publishers = repo.get_publishers()
    assert len(publishers) == 5
    assert Publisher("Marvel") in publishers
    assert Publisher("N/A") in publishers


def test_repository_can_retrieve_book_count(session_factory):
    repo = SqlAlchemyRepository(session_factory)
    number_of_books = repo.get_number_of_books()

    # Check that the query returned 5 books.
    assert number_of_books == 5


def test_repository_does_not_retrieve_a_non_existent_user(session_factory):
    repo = SqlAlchemyRepository(session_factory)
    user = repo.get_user('prince')
    assert user is None


def test_repository_can_add_a_author(session_factory):
    repo = SqlAlchemyRepository(session_factory)
    author = Author(123, 'dave')
    assert repo.get_author(123) is None
    repo.add_author(author)

    assert repo.get_author(123) is author


def test_repository_can_retrieve_a_author(session_factory):
    repo = SqlAlchemyRepository(session_factory)
    author = repo.get_author(6384773)
    assert author == Author(6384773, 'Asma')


def test_repository_does_not_retrieve_a_non_existent_author(session_factory):
    repo = SqlAlchemyRepository(session_factory)
    author = repo.get_author(1)
    assert author is None


def test_repository_can_add_a_publisher(session_factory):
    repo = SqlAlchemyRepository(session_factory)
    publisher = Publisher('publisher_name')
    assert publisher not in repo.get_publishers()
    repo.add_publisher(publisher)

    assert publisher in repo.get_publishers()


def test_repository_can_retrieve_publishers(session_factory):
    repo = SqlAlchemyRepository(session_factory)
    publishers = repo.get_publishers()
    assert len(publishers) == 12
    assert Publisher("Marvel") in publishers
    assert Publisher("N/A") in publishers


def test_repository_can_retrieve_book_count(session_factory):
    repo = SqlAlchemyRepository(session_factory)
    number_of_books = repo.get_number_of_books()

    assert number_of_books == 20


def test_repository_can_add_book(session_factory):
    repo = SqlAlchemyRepository(session_factory)
    book = Book(
        1,
        'book_title'
    )
    repo.add_book(book)

    assert repo.get_book(1) is book


def test_repository_can_retrieve_book(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    book = repo.get_book(17405342)

    # Check that the Book has the expected title.
    assert book.title == 'Seiyuu-ka! 12'
    assert book.publisher.name == "Hakusensha"


def test_repository_does_not_retrieve_a_non_existent_book(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    book = repo.get_book(1)
    assert book is None


def test_repository_can_retrieve_books_by_year(session_factory):
    repo = SqlAlchemyRepository(session_factory)
    books = repo.get_books_by_year(2013)
    # Check that the query returned 1 Books.
    assert len(books) == 1
    assert books[0].title == "Seiyuu-ka! 12"


def test_repository_does_not_retrieve_an_book_when_there_are_no_books_for_a_given_date(session_factory):
    repo = SqlAlchemyRepository(session_factory)
    books = repo.get_books_by_year(1900)
    assert len(books) == 0


def test_repository_can_retrieve_books_after_year(session_factory):
    repo = SqlAlchemyRepository(session_factory)
    # book year in test data are N/A, 2006, 2006, 2011, 2013 respectively
    books = repo.get_books_after_year_inclusive(2010)
    # Check that the query returned 1 Books.

    assert books[0].title == 'Sherlock Holmes: Year One' or books[1].title == 'Sherlock Holmes: Year One'

    # check year value is inclusive
    books = repo.get_books_after_year_inclusive(2011)
    # Check that the query returned 1 Books.
    assert books[0].title == 'Sherlock Holmes: Year One' or books[1].title == 'Sherlock Holmes: Year One'


def test_repository_can_get_books_by_ids(session_factory):
    repo = SqlAlchemyRepository(session_factory)
    books = repo.get_books_by_id([13340336, 2168737])

    assert len(books) == 2
    assert books[0].title == '20th Century Boys, Libro 15: ¡Viva la Expo! (20th Century Boys, #15)'
    assert books[1].title == "The Thing: Idol of Millions"


def test_repository_does_not_retrieve_book_for_non_existent_id(session_factory):
    repo = SqlAlchemyRepository(session_factory)
    books = repo.get_books_by_id([18955715, 3])

    assert len(books) == 1
    assert books[0].title == 'D.Gray-man, Vol. 16: Blood \u0026 Chains'


def test_repository_returns_an_empty_list_for_non_existent_ids(session_factory):
    repo = SqlAlchemyRepository(session_factory)
    books = repo.get_books_by_id([0, 9])

    assert len(books) == 0


def test_repository_returns_book_id_for_publisher(session_factory):
    repo = SqlAlchemyRepository(session_factory)
    book_ids = repo.get_book_ids_for_publisher(Publisher("Hakusensha"))
    assert len(book_ids) == 1
    books = repo.get_books_by_id(book_ids)
    assert len(books) == 1
    assert books[0].title == "Seiyuu-ka! 12"


def test_repository_can_add_a_review(session_factory):
    repo = SqlAlchemyRepository(session_factory)
    user = repo.get_user('ftinson0')
    book = repo.get_books_by_id([13340336])[0]
    review = Review(book, "Trump's onto it!", 3)

    user.add_review(review)
    repo.add_review(review, user)

    assert review in repo.get_reviews()
    assert review in repo.get_reviews_for_book(book)


def test_repository_does_not_add_a_review_without_a_user(session_factory):
    repo = SqlAlchemyRepository(session_factory)
    book = repo.get_books_by_id([13340336])[0]
    review = Review(book, "Trump's onto it!", 3)
    user = repo.get_user('ftinson0')

    with pytest.raises(RepositoryException):
        repo.add_review(review, user)


def test_repository_does_sync_add_a_review_without_a_valid_book(session_factory):
    repo = SqlAlchemyRepository(session_factory)
    user = repo.get_user('ftinson0')
    book = Book(1, 'title')
    review = Review(book, "Trump's onto it!", 3)

    user.add_review(review)

    repo.add_review(review, user)
    book_1 = repo.get_book(1)

    assert book_1 == book

#needs fixing
def test_repository_can_retrieve_reviews(session_factory):
    repo = SqlAlchemyRepository(session_factory)
    book = repo.get_book(30128855)
    review = Review(
        book,
        ''"Fusce posuere felis sed lacus. Morbi sem mauris, laoreet ut, rhoncus aliquet, pulvinar sed, nisl."'',
        2,
        timestamp=datetime.fromisoformat("2021-09-04 09:29:14")
    )
    assert len(repo.get_reviews()) == 201
    assert len(repo.get_reviews_for_book(book)) == 15
    assert review == repo.get_reviews()[0]
    assert review == repo.get_reviews_for_book(book)[0]


#  remove because inventory is not used
# def test_repository_can_retrieve_book_inventory(session_factory):
#     repo = SqlAlchemyRepository(session_factory)
#     inventory = repo.get_books_inventory()
#     assert inventory is not None
#     assert inventory.find_book(17405342).book_id == 17405342
#     assert inventory.find_price(17405342) == 17.4
#     assert inventory.find_stock_count(17405342) == 42

#needs fixing
def test_get_author_by_name(session_factory):
    repo = SqlAlchemyRepository(session_factory)
    name = "Takashi   Murakami"
    author = repo.get_author_by_name(name)
    assert author is not None
    assert author.unique_id == 6869276
