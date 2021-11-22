from itertools import permutations
from typing import List

import pytest, datetime
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import with_polymorphic, selectin_polymorphic

from library.domain.model import User, Publisher, Book, Review, make_review, Author, ReadingList, BundledReadingList, \
    ReadReadingList, Shelve


def insert_user(empty_session, values=None):
    new_name = "andrew"
    new_password = "12345678"
    new_pages_read = 0

    if values is not None:
        new_name = values[0]
        new_password = values[1]
        new_pages_read = values[2]

    empty_session.execute(
        'INSERT INTO user (user_name, password, pages_read) VALUES (:user_name, :password, :pages_read)',
        {'user_name': new_name, 'password': new_password, 'pages_read': new_pages_read})
    row = empty_session.execute('SELECT id from user where user_name = :user_name',
                                {'user_name': new_name}).fetchone()
    return row[0]


def insert_users(empty_session, values):
    for value in values:
        empty_session.execute(
            'INSERT INTO user (user_name, password, pages_read) VALUES (:user_name, :password, :pages_read)',
            {'user_name': value[0], 'password': value[1], 'pages_read': value[2]})
    rows = list(empty_session.execute('SELECT id from user'))
    keys = tuple(row[0] for row in rows)
    return keys


def insert_publisher(empty_session, values=None):
    new_name = "pub"

    if values is not None:
        new_name = values[0]

    empty_session.execute(
        'INSERT INTO publisher (name) VALUES (:name)',
        {'name': new_name})
    row = empty_session.execute('SELECT id from publisher where name = :name',
                                {'name': new_name}).fetchone()
    return row[0]


def insert_publishers(empty_session, values):
    for value in values:
        empty_session.execute(
            'INSERT INTO publisher (name) VALUES (:name)',
            {'name': value[0]})
    rows = list(empty_session.execute('SELECT id from publisher'))
    keys = tuple(row[0] for row in rows)
    return keys


def insert_book(empty_session):
    publisher_key = insert_publisher(empty_session)
    empty_session.execute(
        'INSERT INTO book ('
        'id,website_url,ebook,num_pages,title,publisher_id,image_url,'
        'description,release_year,average_rating,rating_count,text_reviews_count) VALUES '
        '(5, "", 1, 2, "title_", :publisher, "",'
        '"description_", 2048, 1.2, 3, 4)',
        {'publisher': publisher_key}
    )
    row = empty_session.execute('SELECT id from book').fetchone()
    return row[0]


def insert_authors(empty_session, names):
    for name in names:
        empty_session.execute(
            'INSERT INTO author (full_name, average_rating, rating_count, text_reviews_count) VALUES'
            '(:name, 1, 2, 3)',
            {'name': name}
        )

    rows = list(empty_session.execute('SELECT id from author'))
    keys = tuple(row[0] for row in rows)
    return keys


def insert_reviewed_book(empty_session):
    book_key = insert_book(empty_session)
    user_key = insert_user(empty_session)

    timestamp_1 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    timestamp_2 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    empty_session.execute(
        'INSERT INTO review (book_id, text, rating, timestamp, user_id) VALUES '
        '(:user_id, "review_text_", :book_id, 2, :timestamp1),'
        '(:user_id, "review_text_2", :book_id, 2, :timestamp2)',
        {'user_id': user_key, 'book_id': book_key, 'timestamp1': timestamp_1, 'timestamp2': timestamp_2}
    )
    row = empty_session.execute('SELECT id from review').fetchone()
    return row[0]


def insert_read_book(empty_session):
    book_key = insert_book(empty_session)
    user_key = insert_user(empty_session)

    empty_session.execute(
        'INSERT INTO user_books_read (book_id, user_id) VALUES '
        '(:book_id, :user_id)',
        {'user_id': user_key, 'book_id': book_key}
    )


def insert_authored_book(empty_session):
    book_key = insert_book(empty_session)
    author_keys = insert_authors(empty_session, ['author1', 'author2'])

    for author_key in author_keys:
        empty_session.execute(
            'INSERT INTO book_author (book_id, author_id) VALUES '
            '(:book_id, :author_id)',
            {'author_id': author_key, 'book_id': book_key}
        )


def insert_reading_list(empty_session, ids, poly_identities=None):
    if poly_identities is None:
        poly_identities = ['base'] * len(ids)
    for id, poly_identity in zip(ids, poly_identities):
        empty_session.execute(
            'INSERT INTO reading_list ('
            'id,name,is_public, type) VALUES '
            '(:id, :name, 1, :type)',
            {'id': id, 'type': poly_identity, 'name': "list_name_%d" % id}
        )


def insert_bundled_list_relationship(empty_session, ids):
    for a, b in permutations(ids, 2):
        empty_session.execute(
            'INSERT INTO bundled_list (list_id_a, list_id_b) VALUES'
            '(:id_a, :id_b)',
            {'id_a': a, 'id_b': b}
        )


def insert_book_to_reading_list(empty_session, reading_list_id, book_id):
    empty_session.execute(
        'INSERT INTO reading_list_entry (book_id,reading_list_id) VALUES '
        '(:book_id, :reading_list_id)',
        {'book_id': book_id, 'reading_list_id': reading_list_id}
    )


def make_user():
    user = User("andrew", "111111111", 3)
    return user


def make_publisher():
    publisher = Publisher("Andrew")
    return publisher


def make_book(id=5):
    book = Book(id, "title_%d" % id)
    book.publisher = Publisher("pub%d" % id)
    return book


def make_author():
    author = Author(2, "author_name_")
    return author


def make_reading_list():
    reading_list = ReadingList("name_", None)
    return reading_list


def make_bundled_list():
    bundled_list = BundledReadingList("bundled_", None)
    return bundled_list


def make_shelve():
    user = make_user()
    return user.shelve


def test_loading_of_users(empty_session):
    users = list()
    users.append(("andrew", "12345678", 3))
    users.append(("cindy", "11111111", 5))
    insert_users(empty_session, users)
    # case insensitive
    expected = [
        User("Andrew", "12345678", 3),
        User("Cindy", "999", 5)
    ]
    assert empty_session.query(User).all() == expected


def test_saving_of_users(empty_session):
    user = make_user()
    empty_session.add(user)
    empty_session.commit()

    rows = list(empty_session.execute('SELECT user_name, password FROM user'))
    assert rows == [("andrew", "111111111")]


def test_saving_of_users_with_common_user_name(empty_session):
    insert_user(empty_session, ("andrew", "12345678", 8))
    empty_session.commit()

    with pytest.raises(IntegrityError):
        user = User("Andrew", "111111111")
        empty_session.add(user)
        empty_session.commit()


def test_loading_of_publishers(empty_session):
    publishers = list()
    publishers.append(("Andrew",))
    publishers.append(("Cindy",))
    insert_publishers(empty_session, publishers)
    # case insensitive
    expected = [
        Publisher("Andrew"),
        Publisher("Cindy")
    ]
    assert empty_session.query(Publisher).all() == expected


def test_saving_of_publishers(empty_session):
    publisher = make_publisher()
    empty_session.add(publisher)
    empty_session.commit()

    rows = list(empty_session.execute('SELECT name FROM publisher'))
    assert rows == [("Andrew",)]


def test_saving_of_publishers_with_common_publisher_name(empty_session):
    insert_publisher(empty_session, ("Andrew",))
    empty_session.commit()

    with pytest.raises(IntegrityError):
        publisher = Publisher("Andrew")
        empty_session.add(publisher)
        empty_session.commit()


def test_loading_of_book(empty_session):
    book_key = insert_book(empty_session)
    expected_book = make_book()
    fetched_book = empty_session.query(Book).one()

    assert expected_book == fetched_book
    assert book_key == fetched_book.book_id


def test_loading_of_reviewed_book(empty_session):
    insert_reviewed_book(empty_session)

    rows = empty_session.query(Book).all()
    book = rows[0]

    for review in book.reviews:
        assert review.book is book
        assert review.user is not None


def test_loading_of_read_book(empty_session):
    insert_read_book(empty_session)

    user: User = empty_session.query(User).one()
    book: Book = empty_session.query(Book).one()

    assert book in user.read_books


def test_loading_of_authored_book(empty_session):
    insert_authored_book(empty_session)

    book = empty_session.query(Book).one()
    authors = empty_session.query(Author).all()

    assert len(authors) == 2
    assert type(authors[0]) == Author

    for author in authors:
        assert author in book.authors


def test_saving_of_review(empty_session):
    book_key = insert_book(empty_session)
    user_key = insert_user(empty_session, ("andrew", "12345678", 3))

    rows = empty_session.query(Book).all()
    book = rows[0]
    user = empty_session.query(User).filter(User._User__user_name == "andrew").one()

    # Create a new Review that is bidirectionally linked with the User and Book.
    review_text = "Some review text."
    review = make_review(review_text, 3, user, book)

    # Note: if the bidirectional links between the new Review and the User and
    # Book objects hadn't been established in memory, they would exist following
    # committing the addition of the Review to the database.
    empty_session.add(review)
    empty_session.commit()

    rows = list(empty_session.execute('SELECT user_id, book_id, text, rating FROM review'))

    assert rows == [(user_key, book_key, review_text, 3)]


def test_saving_of_book(empty_session):
    book = make_book()
    empty_session.add(book)
    empty_session.commit()
    rows = list(
        empty_session.execute('SELECT id,website_url,ebook,num_pages,title,image_url FROM book'))
    assert rows == [(5, "", 0, 0, "title_5", "")]


def test_saving_read_book(empty_session):
    book = make_book()
    user = make_user()

    user.read_a_book(book)

    # Persist the Book (and Tag).
    # Note: it doesn't matter whether we add the Tag or the Book. They are connected
    # bidirectionally, so persisting either one will persist the other.
    empty_session.add(book)
    empty_session.add(user)
    empty_session.commit()

    # Test test_saving_of_book() checks for insertion into the books table.
    rows = list(empty_session.execute('SELECT id FROM book'))
    book_key = rows[0][0]

    # Check that the user table has a new record.
    rows = list(empty_session.execute('SELECT id, user_name FROM user'))
    user_key = rows[0][0]
    assert rows[0][1] == "andrew"

    # Check that the book_tags table has a new record.
    rows = list(empty_session.execute('SELECT book_id, user_id from user_books_read'))
    book_foreign_key = rows[0][0]
    user_foreign_key = rows[0][1]

    assert book_key == book_foreign_key
    assert user_key == user_foreign_key


def test_save_reviewed_book(empty_session):
    # Create Book User objects.
    book = make_book()
    user = make_user()

    # Create a new Review that is bidirectionally linked with the User and Book.
    review_text = "Some review text."
    review = make_review(review_text, 3, user, book)

    # Save the new Book.
    empty_session.add(book)
    empty_session.commit()

    # Test test_saving_of_book() checks for insertion into the books table.
    rows = list(empty_session.execute('SELECT id FROM book'))
    book_key = rows[0][0]

    # Test test_saving_of_users() checks for insertion into the users table.
    rows = list(empty_session.execute('SELECT id FROM user'))
    user_key = rows[0][0]

    # Check that the reviews table has a new record that links to the books and users
    # tables.
    rows = list(empty_session.execute('SELECT user_id, book_id, text, rating FROM review'))
    assert rows == [(user_key, book_key, review_text, 3)]


def test_save_authored_book(empty_session):
    author = make_author()
    book = make_book()

    book.add_author(author)
    empty_session.add(author)
    empty_session.add(book)
    empty_session.commit()

    # Test test_saving_of_book() checks for insertion into the books table.
    rows = list(empty_session.execute('SELECT id FROM book'))
    book_key = rows[0][0]

    # Test test_saving_of_users() checks for insertion into the users table.
    rows = list(empty_session.execute('SELECT id FROM author'))
    author_key = rows[0][0]

    # Check that the reviews table has a new record that links to the books and users
    # tables.
    rows = list(empty_session.execute('SELECT author_id, book_id FROM book_author'))
    assert rows == [(author_key, book_key)]


def test_loading_of_reading_lists(empty_session):
    # make lists
    list_keys = [1, 2, 3]
    identities = ['base', 'bundled', 'read']
    insert_reading_list(empty_session, list_keys, identities)
    insert_bundled_list_relationship(empty_session, [2, 3])
    book_key = insert_book(empty_session)
    for list_key in list_keys:
        insert_book_to_reading_list(empty_session, list_key, book_key)

    # check existence of reading list
    # cls = with_polymorphic(ReadingList, [BundledReadingList, ReadReadingList])
    reading_lists: List[ReadingList] = empty_session.query(ReadingList).all()
    book = empty_session.query(Book).one()
    assert len(reading_lists) == 3
    assert isinstance(reading_lists[0], ReadingList)
    assert not isinstance(reading_lists[0], BundledReadingList)
    assert isinstance(reading_lists[1], BundledReadingList)
    assert isinstance(reading_lists[2], ReadReadingList)

    # check attached book
    reading_list = reading_lists[0]
    assert len(reading_list.books) == 1
    assert reading_lists[0].books == reading_list.books
    assert reading_list.books == [book]
    assert reading_lists[2].books == [book]

    # cannot add duplicated books
    with pytest.raises(IntegrityError):
        insert_book_to_reading_list(empty_session, list_keys[0], book_key)

    # query subtype
    reading_lists = empty_session.query(ReadingList).filter_by(type="read").all()
    assert len(reading_lists) == 1

    # check bundling
    reading_lists: List[BundledReadingList] = empty_session.query(ReadingList). \
        filter((ReadingList.type == "bundled") | (ReadingList.type == "read")).all()
    assert len(reading_lists) == 2
    assert isinstance(reading_lists[0], BundledReadingList)
    assert isinstance(reading_lists[1], ReadingList)

    list_0 = reading_lists[0]
    list_1 = reading_lists[1]
    bundled_lists = list_0._BundledReadingList__bundled_reading_lists
    assert len(bundled_lists) == 1
    assert bundled_lists[0] == list_1

    # query subtype info
    reading_lists = empty_session.query(ReadingList) \
        .options(selectin_polymorphic(ReadingList, [BundledReadingList, ReadReadingList])).all()
    assert len(reading_lists) == 3


def test_saving_of_reading_lists(empty_session):
    book1 = make_book(3)
    book2 = make_book(4)

    list_1 = make_reading_list()
    bundle_1 = make_bundled_list()
    bundle_2 = make_bundled_list()

    bundle_1.add_book(book1)
    bundle_2.add_book(book2)
    list_1.add_book(book1)
    list_1.add_book(book2)

    bundle_1.bundle(bundle_2)
    bundle_2.bundle(bundle_1)

    empty_session.add_all([book1, book2, list_1, bundle_1, bundle_2])
    empty_session.commit()

    # checks reading_lists
    list_rows = list(empty_session.execute('SELECT id, type FROM reading_list'))
    assert len(list_rows) == 3
    # Order: list1, bundle1, bundle2
    assert list_rows[0][1] == 'base'
    assert list_rows[1][1] == 'bundled'

    # check books
    list_book_rows = list(empty_session.execute('SELECT book_id, reading_list_id FROM reading_list_entry'))
    assert len(list_book_rows) == 4
    assert (book1.book_id, list_rows[1][0]) in list_book_rows
    assert (book2.book_id, list_rows[0][0]) in list_book_rows

    # check bundling
    bunlding_rows = list(empty_session.execute('SELECT list_id_a, list_id_b FROM bundled_list'))
    assert len(bunlding_rows) == 2
    # check for bi-directional bundling
    assert (list_rows[1][0], list_rows[2][0]) in bunlding_rows
    assert (list_rows[2][0], list_rows[1][0]) in bunlding_rows

    # check mutual exclusion of bondled lists
    # adding book2 (existing in bundle_2 atm) to bundle_1 should remove it from bundle_2
    bundle_1.add_book(book2)
    empty_session.commit()

    stmt = 'SELECT book_id FROM reading_list_entry WHERE reading_list_id=%d'
    list_book_rows = list(empty_session.execute(stmt % list_rows[1][0]))
    assert list_book_rows == [(book1.book_id,), (book2.book_id,)]
    list_book_rows = list(empty_session.execute(stmt % list_rows[2][0]))
    assert list_book_rows == []


def test_saving_loading_shelve(empty_session):
    # check saving
    user = make_user()
    shelve = user.shelve
    empty_session.add(user)
    empty_session.commit()

    # check shelve table
    row = empty_session.execute('SELECT * FROM shelve').fetchone()
    assert None not in row

    # check reading lists
    rows = empty_session.execute('SELECT shelve_id FROM reading_list').fetchall()
    assert len(rows) == 3
    for row in rows:
        assert row[0] == 1

    # check bundling
    row = empty_session.execute('SELECT COUNT(*) FROM bundled_list').fetchone()
    assert row[0] == 6

    # check loading
    shelve: Shelve = empty_session.query(Shelve).one()
    # check existence of reading lists
    assert len(shelve.to_read_list) == 0
    assert type(shelve.currently_reading_list) == BundledReadingList
    assert len(shelve.reading_lists) == 3
    assert shelve.read_list in shelve.reading_lists

    assert shelve.user == user
    # check bundling
    assert shelve.to_read_list.is_bundled_with(shelve.read_list)
