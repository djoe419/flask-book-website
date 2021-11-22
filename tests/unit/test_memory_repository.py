import datetime

import pytest

from library.adapters.repository import RepositoryException
from library.domain.model import User, Author, Publisher, Book, Review


# user section
def test_repository_can_add_a_user(in_memory_repo):
    user = User('dave', '123456789')
    assert in_memory_repo.get_user('dave') is None
    in_memory_repo.add_user(user)

    assert in_memory_repo.get_user('dave') is user


def test_repository_can_retrieve_a_user(in_memory_repo):
    user = in_memory_repo.get_user("jreede0")
    assert user == User('jreede0', 'Gk8thq')
    assert user.pages_read == 1239
    assert len(user.read_books) == 3
    assert user.read_books[0].book_id == 13340336


def test_repository_does_not_retrieve_a_non_existent_user(in_memory_repo):
    user = in_memory_repo.get_user('prince')
    assert user is None


#   author section
def test_repository_can_add_a_author(in_memory_repo):
    author = Author(123, 'dave')
    assert in_memory_repo.get_author(123) is None
    in_memory_repo.add_author(author)

    assert in_memory_repo.get_author(123) is author


def test_repository_can_retrieve_a_author(in_memory_repo):
    author = in_memory_repo.get_author(6384773)
    assert author == Author(6384773, 'Asma')


def test_repository_does_not_retrieve_a_non_existent_author(in_memory_repo):
    author = in_memory_repo.get_author(1)
    assert author is None
    
  
#   publisher section
#   author section
def test_repository_can_add_a_publisher(in_memory_repo):
    publisher = Publisher('publisher_name')
    assert publisher not in in_memory_repo.get_publishers()
    in_memory_repo.add_publisher(publisher)

    assert publisher in in_memory_repo.get_publishers()


def test_repository_can_retrieve_publishers(in_memory_repo):
    publishers = in_memory_repo.get_publishers()
    assert len(publishers) == 5
    assert Publisher("Marvel") in publishers
    assert Publisher("N/A") in publishers


# book section
def test_repository_can_retrieve_book_count(in_memory_repo):
    number_of_books = in_memory_repo.get_number_of_books()

    # Check that the query returned 5 books.
    assert number_of_books == 5


def test_repository_can_add_book(in_memory_repo):
    book = Book(
        1,
        'book_title'
    )
    in_memory_repo.add_book(book)

    assert in_memory_repo.get_book(1) is book


# noinspection SpellCheckingInspection
def test_repository_can_retrieve_book(in_memory_repo):
    book = in_memory_repo.get_book(17405342)

    # Check that the Book has the expected title.
    assert book.title == 'Seiyuu-ka! 12'
    assert book.publisher.name == "Hakusensha"


def test_repository_does_not_retrieve_a_non_existent_book(in_memory_repo):
    book = in_memory_repo.get_book(1)
    assert book is None


def test_repository_can_retrieve_books_by_year(in_memory_repo):
    books = in_memory_repo.get_books_by_year(2013)
    # Check that the query returned 1 Books.
    assert len(books) == 1
    assert books[0].title == "Seiyuu-ka! 12"


def test_repository_does_not_retrieve_an_book_when_there_are_no_books_for_a_given_date(in_memory_repo):
    books = in_memory_repo.get_books_by_year(1900)
    assert len(books) == 0


def test_repository_can_retrieve_books_after_year(in_memory_repo):
    # book year in test data are N/A, 2006, 2006, 2011, 2013 respectively
    books = in_memory_repo.get_books_after_year_inclusive(2010)
    # Check that the query returned 1 Books.
    assert len(books) == 2
    assert books[0].title == "Seiyuu-ka! 12" or books[1].title == "Seiyuu-ka! 12"

    # check year value is inclusive
    books = in_memory_repo.get_books_after_year_inclusive(2011)
    # Check that the query returned 1 Books.
    assert len(books) == 2
    assert books[0].title == "Seiyuu-ka! 12" or books[1].title == "Seiyuu-ka! 12"


def test_repository_can_get_books_by_ids(in_memory_repo):
    books = in_memory_repo.get_books_by_id([13340336, 2168737])

    assert len(books) == 2
    assert books[0].title == '20th Century Boys, Libro 15: ¡Viva la Expo! (20th Century Boys, #15)'
    assert books[1].title == "The Thing: Idol of Millions"


def test_repository_does_not_retrieve_book_for_non_existent_id(in_memory_repo):
    books = in_memory_repo.get_books_by_id([18955715, 3])

    assert len(books) == 1
    assert books[0].title == 'D.Gray-man, Vol. 16: Blood \u0026 Chains'


def test_repository_returns_an_empty_list_for_non_existent_ids(in_memory_repo):
    books = in_memory_repo.get_books_by_id([0, 9])

    assert len(books) == 0


def test_repository_returns_book_id_for_publisher(in_memory_repo):
    book_ids = in_memory_repo.get_book_ids_for_publisher(Publisher("Hakusensha"))
    assert len(book_ids) == 1
    books = in_memory_repo.get_books_by_id(book_ids)
    assert len(books) == 1
    assert books[0].title == "Seiyuu-ka! 12"


def test_repository_can_add_a_review(in_memory_repo):
    user = in_memory_repo.get_user('jreede0')
    book = in_memory_repo.get_books_by_id([13340336])[0]
    review = Review(book, "Trump's onto it!", 3)

    user.add_review(review)
    in_memory_repo.add_review(review, user)

    assert review in in_memory_repo.get_reviews()
    assert review in in_memory_repo.get_reviews_for_book(book)


def test_repository_does_not_add_a_review_without_a_user(in_memory_repo):
    book = in_memory_repo.get_books_by_id([13340336])[0]
    review = Review(book, "Trump's onto it!", 3)
    user = in_memory_repo.get_user('jreede0')

    with pytest.raises(RepositoryException):
        in_memory_repo.add_review(review, user)


def test_repository_does_not_add_a_review_without_a_valid_book(in_memory_repo):
    user = in_memory_repo.get_user('jreede0')
    book = Book(1, 'title')
    review = Review(book, "Trump's onto it!", 3)

    user.add_review(review)

    with pytest.raises(RepositoryException):
        # Exception expected because the book is not in the database
        in_memory_repo.add_review(review, user)


def test_repository_can_retrieve_reviews(in_memory_repo):
    book = in_memory_repo.get_book(18955715)
    review = Review(
        book,
        '''Maecenas tristique, est et tempus semper, est quam pharetra magna, ac consequat metus sapien ut nunc. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia Curae; Mauris viverra diam vitae quam.''',
        2,
        timestamp=datetime.datetime.fromisoformat("2020-10-23 19:35:30")
    )
    assert len(in_memory_repo.get_reviews()) == 10
    assert len(in_memory_repo.get_reviews_for_book(book)) == 4
    assert review == in_memory_repo.get_reviews()[4]
    assert review == in_memory_repo.get_reviews_for_book(book)[2]


# remove because inventory is not used
# def test_repository_can_retrieve_book_inventory(in_memory_repo):
#     inventory = in_memory_repo.get_books_inventory()
#     assert inventory is not None
#     assert inventory.find_book(17405342).book_id == 17405342
#     assert inventory.find_price(17405342) == 17.4
#     assert inventory.find_stock_count(17405342) == 42


def test_get_author_by_name(in_memory_repo):
    name = "Takashi   Murakami"
    author = in_memory_repo.get_author_by_name(name)
    assert author is not None
    assert author.unique_id == 6869276
