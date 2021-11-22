from library.books.services import book_to_dict
from library.domain.model import User


def user_to_dict(user: User):
    return {
        'name': user.user_name,
        'read_books_num': len(user.read_books),
        'reviews_written': len(user.reviews),
        'pages_read': user.pages_read,
    }