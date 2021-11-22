from sqlalchemy import select, inspect, false, true

from library.adapters.orm import metadata


def test_database_populate_inspect_table_names(database_engine):
    # Get table information
    inspector = inspect(database_engine)
    assert inspector.get_table_names() == [
        'author', 'book', 'book_author',
        'bundled_list',
        'publisher',
        'reading_list',
        'reading_list_entry',
        'review',
        'shelve',
        'user',
        'user_books_read'
    ]


def test_database_populate_select_all_users(database_engine):
    # Get table information
    inspector = inspect(database_engine)
    name_of_users_table = inspector.get_table_names()[9]

    with database_engine.connect() as connection:
        # query for records in table users
        select_statement = select([metadata.tables[name_of_users_table]])
        result = connection.execute(select_statement)

        all_users = []
        for row in result:
            all_users.append(row['user_name'])

        assert all_users == ['jreede0', 'vsneaker1', 'celcoux2', 'jviveash3', 'lcroisdall4', 'nscotfurth5',
                             'dfass6', 'njagiello7', 'kbuye8', 'bbragg9']


# not sure if publisher names are correct.
def test_database_populate_select_all_publishers(database_engine):
    inspector = inspect(database_engine)
    name_of_publisher_table = inspector.get_table_names()[4]

    with database_engine.connect() as connection:
        # query for records in table tags
        select_statement = select([metadata.tables[name_of_publisher_table]])
        result = connection.execute(select_statement)

        all_publishers = []
        for row in result:
            all_publishers.append(row['publisher_name'])

        assert all_publishers == [
            'Hakusensha',
            'Planeta DeAgostini',
            'Shi Bao Wen Hua Chu Ban Qi Ye Gu Fen You Xian Gong Si',
            'Marvel',
            'N/A'
        ]


# needs work
def test_database_populate_select_all_books(database_engine):
    inspector = inspect(database_engine)
    name_of_books_table = inspector.get_table_names()[1]

    with database_engine.connect() as connection:
        # query for records in table tags
        select_statement = select([metadata.tables[name_of_books_table]])
        result = connection.execute(select_statement)

        all_books = []
        for row in result:
            all_books.append((row['id'], row['website_url'], row['ebook'], row['num_pages'], row['title']))

        assert all_books[0][:5] == (2168737, "https://www.goodreads.com/book/show/2168737.The_Thing", 0, 192,
                                    "The Thing: Idol of Millions")


def test_database_populate_select_all_reviews(database_engine):
    inspector = inspect(database_engine)
    name_of_reviews_table = inspector.get_table_names()[7]

    with database_engine.connect() as connection:
        # query for records in table tags
        select_statement = select([metadata.tables[name_of_reviews_table]])
        result = connection.execute(select_statement)

        all_reviews = []
        for row in result:
            all_reviews.append((row['id'], row['book_id'], row['text'], row['rating'], row['timestamp'].isoformat()))

        nr_reviews = len(all_reviews)
        assert nr_reviews == 10

        assert all_reviews[0] == (1, 18711343, 'Duis aliquam convallis nunc. Proin at turpis a pede posuere nonummy.',
                                               2, '2021-06-14T05:22:06')


def test_database_populate_select_all_shelves(database_engine):
    inspector = inspect(database_engine)
    name_of_shelves_table = inspector.get_table_names()[8]

    with database_engine.connect() as connection:
        # query for records in table tags
        select_statement = select([metadata.tables[name_of_shelves_table]])
        result = connection.execute(select_statement)

        all_shelves = []
        for row in result:
            all_shelves.append((row['id'], row['user_id'], row['to_read'], row['current'], row['read']))

        nr_shelves = len(all_shelves)
        assert nr_shelves == 10

        assert all_shelves[0][:2] == (1, 1)
        for value in all_shelves[0]:
            assert value > 0


def test_database_populate_select_all_reading_lists(database_engine):
    inspector = inspect(database_engine)
    name_of_reading_list_table = inspector.get_table_names()[5]

    with database_engine.connect() as connection:
        # query for records in table tags
        select_statement = select([metadata.tables[name_of_reading_list_table]])
        result = connection.execute(select_statement)

        all_reading_lists = []
        for row in result:
            all_reading_lists.append((row['id'], row['name'], row['is_public'], row['type'], row['shelve_id']))

        nr_reading_lists = len(all_reading_lists)
        assert nr_reading_lists == 43

        assert all_reading_lists[0][1:] == ('sit', 0, 'bundled', 1)


def test_database_populate_select_all_author(database_engine):
    inspector = inspect(database_engine)
    name_of_authors_table = inspector.get_table_names()[0]

    with database_engine.connect() as connection:
        # query for records in table tags
        select_statement = select([metadata.tables[name_of_authors_table]])
        result = connection.execute(select_statement)

        all_authors = []
        for row in result:
            all_authors.append(row['full_name'])

        assert all_authors == [
            'Dan Slott',
            'Eric Ethan',
            'Andrea DiVito',
            'Kieron Dwyer',
            'Naoki Urasawa',
            'Katsura Hoshino',
            'Maki Minami',
            'Asma',
            'Takashi   Murakami',
            'Cun Shang Chong'
        ]


def test_database_populate_select_all_book_author(database_engine):
    inspector = inspect(database_engine)
    name_of_book_author_table = inspector.get_table_names()[2]

    with database_engine.connect() as connection:
        # query for records in table tags
        select_statement = select([metadata.tables[name_of_book_author_table]])
        result = connection.execute(select_statement)

        all_book_author = []
        for row in result:
            all_book_author.append((row['book_id'], row['author_id']))

        nr_author_id = len(all_book_author)
        assert nr_author_id == 9

        assert all_book_author[0] == (17405342, 791996)


# needs work
def test_database_populate_select_all_user_books_read(database_engine):
    inspector = inspect(database_engine)
    name_of_books_table = inspector.get_table_names()[10]

    with database_engine.connect() as connection:
        # query for records in table tags
        select_statement = select([metadata.tables[name_of_books_table]])
        result = connection.execute(select_statement)

        all_books = []
        for row in result:
            all_books.append((row['book_id'], row['user_id']))

        nr_user_books_read = len(all_books)
        # real db data change with time
        assert nr_user_books_read >= 23

        assert all_books[0] == (13340336, 1)


def test_database_populate_select_all_bundled_list(database_engine):
    inspector = inspect(database_engine)
    name_of_bundled_list = inspector.get_table_names()[3]

    with database_engine.connect() as connection:
        # query for records in table tags
        select_statement = select([metadata.tables[name_of_bundled_list]])
        result = connection.execute(select_statement)

        all_bundled_list = []
        for row in result:
            all_bundled_list.append((row['list_id_a'], row['list_id_b']))

        nr_user_bundled_list = len(all_bundled_list)
        assert nr_user_bundled_list == 60

        for value in all_bundled_list[0]:
            assert value > 0
