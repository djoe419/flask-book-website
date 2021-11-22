from sqlalchemy import (
    Table, MetaData, Column, Integer, String, Date, DateTime,
    ForeignKey, UniqueConstraint, Boolean
)
from sqlalchemy.orm import mapper, relationship, synonym, backref

from library.domain import model

# global variable giving access to the MetaData (schema) information of the database
metadata = MetaData()

users_table = Table(
    'user', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('user_name', String(255), unique=True, nullable=False),
    Column('password', String(255), nullable=False),
    Column('pages_read', Integer, nullable=False),
)

publishers_table = Table(
    'publisher', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', String(255), nullable=False, unique=True)
)

books_table = Table(
    'book', metadata,
    Column('id', Integer, primary_key=True),
    Column('website_url', String(255), nullable=False),
    Column('ebook', Boolean, nullable=False),
    Column('num_pages', Integer, nullable=False),
    Column('title', String(255), nullable=False, unique=True),
    Column('publisher_id', ForeignKey('publisher.id')),
    Column('image_url', String(255), nullable=False),
    Column('description', String(1024), nullable=False),
    Column('release_year', Integer, nullable=False),
    Column('average_rating', Integer, nullable=False),
    Column('rating_count', Integer, nullable=False),
    Column('text_reviews_count', Integer, nullable=False)
)

reviews_table = Table(
    'review', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('book_id', Integer, ForeignKey('book.id')),
    Column('user_id', Integer, ForeignKey('user.id')),
    Column('text', String(512), nullable=False),
    Column('rating', Integer, nullable=False),
    Column('timestamp', DateTime, nullable=False),
)

authors_table = Table(
    'author', metadata,
    Column('id', Integer, primary_key=True),
    Column('full_name', String(255), nullable=False),
    Column('average_rating', Integer, nullable=False),
    Column('rating_count', Integer, nullable=False),
    Column('text_reviews_count', Integer, nullable=False)
)

book_authors_table = Table(
    'book_author', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('book_id', ForeignKey('book.id')),
    Column('author_id', ForeignKey('author.id'))
)

user_books_read_table = Table(
    'user_books_read', metadata,
    # Column('id', Integer, primary_key=True, autoincrement=True),
    Column('book_id', ForeignKey('book.id'), primary_key=True),
    Column('user_id', ForeignKey('user.id'), primary_key=True)
)

reading_lists_table = Table(
    'reading_list', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', String(255), nullable=False),
    Column('is_public', Boolean, nullable=False),
    Column('type', String(10), nullable=False),
    Column('shelve_id', Integer, ForeignKey('shelve.id'))
)

reading_list_entry_table = Table(
    'reading_list_entry', metadata,
    Column('id', Integer, primary_key=True),
    Column('book_id', ForeignKey('book.id')),
    Column('reading_list_id', ForeignKey('reading_list.id')),
    UniqueConstraint('book_id', 'reading_list_id', name='uix_1'),
)

bundled_reading_list_info = Table(
    'bundled_list', metadata,
    Column('list_id_a', Integer, ForeignKey('reading_list.id')),
    Column('list_id_b', Integer, ForeignKey('reading_list.id')),
)

shelves_table = Table(
    'shelve', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('user_id', ForeignKey('user.id')),
    Column('to_read', ForeignKey('reading_list.id'), nullable=True),
    Column('current', ForeignKey('reading_list.id'), nullable=True),
    Column('read', ForeignKey('reading_list.id'), nullable=True)

)


def map_model_to_tables():
    mapper(model.User, users_table, properties={
        '_User__user_name': users_table.c.user_name,
        '_User__password': users_table.c.password,
        '_User__pages_read': users_table.c.pages_read,
        '_User__read_books': relationship(model.Book, secondary=user_books_read_table),
        '_User__reviews': relationship(model.Review, backref='_Review__user')
    })

    mapper(model.Publisher, publishers_table, properties={
        '_Publisher__name': publishers_table.c.name,
    })

    mapper(model.Book, books_table, properties={
        '_Book__id': books_table.c.id,
        '_Book__website_url': books_table.c.website_url,
        '_Book__ebook': books_table.c.ebook,
        '_Book__num_pages': books_table.c.num_pages,
        '_Book__title': books_table.c.title,
        '_Book__publisher': relationship(model.Publisher),
        '_Book__img_url': books_table.c.image_url,
        '_Book__description': books_table.c.description,
        '_Book__release_year': books_table.c.release_year,
        '_Reviewed__average_rating': books_table.c.average_rating,
        '_Reviewed__rating_count': books_table.c.rating_count,
        '_Reviewed__text_reviews_count': books_table.c.text_reviews_count,
        '_Book__authors': relationship(model.Author, secondary=book_authors_table),
        '_Book__reviews': relationship(model.Review, backref='_Review__book'),
    })

    mapper(model.Review, reviews_table, properties={
        '_Review__text': reviews_table.c.text,
        '_Review__rating': reviews_table.c.rating,
        '_Review__timestamp': reviews_table.c.timestamp,
    })

    mapper(model.Author, authors_table, properties={
        '_Author__id': authors_table.c.id,
        'full_name': authors_table.c.full_name,
        # '_Author__coauthors': relationship(model.Author, secondary=coauthors_table),
        '_Reviewed__average_rating': authors_table.c.average_rating,
        '_Reviewed__rating_count': authors_table.c.rating_count,
        '_Reviewed__text_reviews_count': authors_table.c.text_reviews_count,
    })

    mapper(
        model.ReadingList,
        reading_lists_table,
        properties={
            '_ReadingList__uid': reading_lists_table.c.id,
            '_ReadingList__name': reading_lists_table.c.name,
            '_ReadingList__is_public': reading_lists_table.c.is_public,
            '_ReadingList__books': relationship(model.Book, secondary=reading_list_entry_table),
            '_ReadingList__shelve': relationship(
                model.Shelve,
                foreign_keys=[reading_lists_table.c.shelve_id],
                backref='_Shelve__reading_lists',
            ),
        },
        polymorphic_on=reading_lists_table.c.type,
        polymorphic_identity='base',
    )

    mapper(
        model.BundledReadingList,
        reading_lists_table,
        properties={
            '_BundledReadingList__bundled_reading_lists': relationship(
                model.BundledReadingList,
                secondary=bundled_reading_list_info,
                primaryjoin=reading_lists_table.c.id == bundled_reading_list_info.c.list_id_a,
                secondaryjoin=reading_lists_table.c.id == bundled_reading_list_info.c.list_id_b,
            ),
        },
        inherits=model.ReadingList,
        polymorphic_identity='bundled',
    )

    mapper(
        model.ReadReadingList,
        reading_lists_table,
        inherits=model.BundledReadingList,
        polymorphic_identity='read',
    )

    mapper(model.Shelve, shelves_table, properties={
        '_Shelve__user': relationship(model.User, backref=backref('_User__shelve', uselist=False), post_update=False),
        '_Shelve__to_read': relationship(model.BundledReadingList, uselist=False,
                                         foreign_keys=[shelves_table.c.to_read], post_update=True),
        '_Shelve__currently_reading': relationship(model.BundledReadingList, uselist=False,
                                                   foreign_keys=[shelves_table.c.current], post_update=True),
        '_Shelve__read': relationship(model.BundledReadingList, uselist=False,
                                      foreign_keys=[shelves_table.c.read], post_update=True),
    })
