from library.adapters.repository import AbstractRepository
from library.domain.model import *


class NonExistentBookException(Exception):
    pass


class UnknownUserException(Exception):
    pass


def add_review(book_id: int, rating: int, review_text: str, user_name: str, repo: AbstractRepository):
    if not (Checks.check_int(rating) and rating <= 5 and 1 <= rating):
        raise ValueError

    if not Checks.check_str(review_text):
        raise ValueError

    book = repo.get_book(book_id)
    if book is None:
        raise NonExistentBookException

    user = repo.get_user(user_name)
    if user is None:
        raise UnknownUserException

    review = Review(book, review_text, rating)
    user.add_review(review)
    repo.add_review(review, user)


def get_book(book_id: int, repo: AbstractRepository):
    book = repo.get_book(book_id)
    if book is None:
        raise NonExistentBookException

    return book_to_dict(book)


def get_books(book_ids: List[int], repo: AbstractRepository):
    books = repo.get_books_by_id(book_ids)
    return [book_to_dict(book) for book in books]


def get_book_ids_by_year(year: int, repo: AbstractRepository, after_year: bool = True):
    """if after_year is set to false, this method will return books published in the year"""
    if not Checks.check_int(year):
        return []
    books = repo.get_books_after_year_inclusive(year) if after_year else repo.get_books_by_year(year)
    return get_ids_for_books(books)


def get_ids_for_books(books: List[Book]):
    return [book.book_id for book in books]


def get_book_ids_by_title(title: str, repo: AbstractRepository):
    book_ids = repo.get_book_ids_by_title(title)
    books = repo.get_books_by_id(book_ids)
    return [book.book_id for book in books]


def get_book_ids_by_author_name(author_name: str, repo: AbstractRepository):
    author = repo.get_author_by_name(author_name)
    if not author:
        return []
    return get_book_ids_by_author(author, repo)


def get_book_ids_by_author(author: Author, repo: AbstractRepository):
    book_ids = repo.get_book_ids_by_author(author)
    return book_ids


def get_book_ids_by_publisher_name(publisher_name: str, repo: AbstractRepository):
    publishers = repo.get_publishers()
    publisher = next((publisher for publisher in publishers if publisher.name.lower() == publisher_name.lower()), None)
    if not publisher:
        return []
    return get_book_ids_by_publisher(publisher, repo)


def get_book_ids_by_publisher(publisher: Publisher, repo: AbstractRepository):
    book_ids = repo.get_book_ids_by_publisher(publisher)
    return book_ids


def get_reviews_for_book(book_id: int, repo: AbstractRepository):
    book = repo.get_book(book_id)
    if book is None:
        raise NonExistentBookException
    reviews = repo.get_reviews_for_book(book)
    return [review_to_dict(review) for review in reviews]


def can_view_reading_list(reading_list: ReadingList, user: User) -> bool:
    # check for validity
    if reading_list is None:
        return False
    # not public and not yours
    if not reading_list.is_public and reading_list.shelve.user != user:
        return False

    return True


def can_modify_reading_list(reading_list: ReadingList, user: User) -> bool:
    # check for validity
    if reading_list is None:
        return False
    # not public and not yours
    if reading_list.shelve.user != user:
        return False

    return True


def make_new_reading_list(name: str, shelve: Shelve, repo: AbstractRepository):
    reading_list = ReadingList(name, shelve)
    shelve.add_reading_list(reading_list)
    repo.add_reading_list(reading_list)
    return reading_list


def remove_reading_list(id: int, repo: AbstractRepository):
    reading_list = repo.get_reading_list_by_id(id)
    if reading_list is not None and not isinstance(reading_list, BundledReadingList):
        repo.remove_reading_list(reading_list.uid)
        reading_list.shelve.remove_reading_list(reading_list)

##########################################
# Convert objects to dict
##########################################

def publisher_to_dict(publisher: Publisher):
    return {
        'name': publisher.name,
    }


def author_to_dict_simple(author: Author):
    return {
        'full_name': author.full_name,
        'id': author.unique_id,
    }


def author_to_dict_full(author: Author):
    return {
        'full_name': author.full_name,
        'id': author.unique_id,
        'average_rating': author.average_rating,
        'rating_count': author.ratings_count,
        'text_reviews_count': author.text_reviews_count,
        # 'coauthors': [author_to_dict_simple(author) for author in author.coauthors],
    }


def book_to_dict(book: Book):
    return {
        'id': book.book_id,
        'ebook': book.ebook,
        'num_pages': book.num_pages,
        'title': book.title,
        'publisher': publisher_to_dict(book.publisher),
        'description': book.description,
        'release_year': book.release_year,
        'average_rating': book.average_rating,
        'rating_count': book.ratings_count,
        'text_reviews_count': book.text_reviews_count,
        'image_url': book.img_url,
        'website_url': book.website_url,
        'authors': [author_to_dict_simple(author) for author in book.authors],
    }


def review_to_dict(review: Review):
    return {
        'rating': review.rating,
        'text': review.review_text,
        'timestamp': review.timestamp.date(),
        'user': review.user.user_name
    }


def reading_list_to_dict(reading_list: ReadingList):
    return {
        'is_permanent': isinstance(reading_list, BundledReadingList),
        'id': reading_list.uid,
        'name': reading_list.name,
        'is_public': reading_list.is_public,
        'books': [book_to_dict(book) for book in reading_list.books],
        'size': len(reading_list)
    }


def shelve_to_dict(shelve: Shelve):
    return {
        'user': shelve.user.user_name,
        'lists': [reading_list_to_dict(readings_list) for readings_list in shelve.reading_lists]
    }


def shelve_to_distinguished_reading_lists(shelve: Shelve):
    return {
        'user': shelve.user.user_name,
        ReadingList.TO_READ_LIST: reading_list_to_dict(shelve.to_read_list),
        ReadingList.CURRENTLY_READING: reading_list_to_dict(shelve.currently_reading_list),
        ReadingList.READ: reading_list_to_dict(shelve.read_list),
        'lists': [
            reading_list_to_dict(readings_list) for readings_list in shelve.reading_lists
            if not isinstance(readings_list, BundledReadingList)
        ]
    }
