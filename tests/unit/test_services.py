import pytest

from library.authentication.services import AuthenticationException

from library.authentication import services as auth_services

from library.books import services as book_services


# test authentication services
def test_can_add_user(in_memory_repo):
    new_user_name = 'jz'
    new_password = 'abcd1A23'

    auth_services.add_user(new_user_name, new_password, in_memory_repo)

    user_as_dict = auth_services.get_user(new_user_name, in_memory_repo)
    assert user_as_dict['user_name'] == new_user_name

    # Check that password has been encrypted.
    assert user_as_dict['password'].startswith('pbkdf2:sha256:')


def test_cannot_add_user_with_existing_name(in_memory_repo):
    user_name = 'jreede0'
    password = 'Gk8thq'

    with pytest.raises(auth_services.NameNotUniqueException):
        auth_services.add_user(user_name, password, in_memory_repo)


def test_authentication_with_valid_credentials(in_memory_repo):
    new_user_name = 'pmccartney'
    new_password = 'abcd1A23'

    auth_services.add_user(new_user_name, new_password, in_memory_repo)
    auth_services.authenticate_user(new_user_name, new_password, in_memory_repo)


def test_authentication_with_invalid_credentials(in_memory_repo):
    new_user_name = 'pmccartney'
    new_password = 'abcd1A23'

    auth_services.add_user(new_user_name, new_password, in_memory_repo)

    with pytest.raises(auth_services.AuthenticationException):
        auth_services.authenticate_user(new_user_name, '0987654321', in_memory_repo)


# test book services
def test_can_get_book(in_memory_repo):
    book_id = 17405342
    book_dict = book_services.get_book(book_id, in_memory_repo)

    assert book_dict['id'] == book_id
    assert book_dict['ebook'] is False
    assert book_dict['num_pages'] == 157
    assert book_dict['title'] == "Seiyuu-ka! 12"
    assert book_dict['publisher'] == {'name': "Hakusensha"}
    assert book_dict[
               'description'] == "Shiro (Hime) akan mundur dari dunia seiyuu setelah mendapat peran utama di \"Sakura iro no Honoo\". Di film itu, ia mendapati bahwa selain Sakura Aoyama, idolanya, Senri Kudou juga akan berakting bersamanya. Di tengah usahanya menyembunyikan perasaan cinta dan berkonsentrasi pada pekerjaan, terjadilah situasi darurat akibat pendalaman karakter bersama Sakura. Kemudian, Senri akhirnya mengetahui identitas \"Shiro\"!\nApakah impian Hime dan kawan-kawan akhirnya terwujud? Ikuti kisahnya di volume terakhir ini!"
    assert book_dict['release_year'] == 2013
    assert book_dict['average_rating'] == 4.31
    assert book_dict['rating_count'] == 174
    assert book_dict['text_reviews_count'] == 12
    assert book_dict['authors'] == [{'full_name': "Maki Minami", 'id': 791996}]


def test_cannot_get_book_with_non_existent_id(in_memory_repo):
    book_id = 7

    # Call the service layer to attempt to retrieve the Article.
    with pytest.raises(book_services.NonExistentBookException):
        book_services.get_book(book_id, in_memory_repo)


def test_get_books_by_ids(in_memory_repo):
    book_ids = [17405342, 1, 2, 18711343]

    book_dicts = book_services.get_books(book_ids, in_memory_repo)
    assert len(book_dicts) == 2
    book_ids = [book_dict['id'] for book_dict in book_dicts]
    assert [17405342, 18711343] == book_ids


@pytest.mark.parametrize(('after_year', 'yr', 'num_of_books'), (
        (True, 2011, 2),
        (True, 2007, 2),
        (True, 2006, 4),
        (False, 2004, 0),
        (False, 2011, 1),
        (False, 2006, 2)
))
def test_get_books_by_yr(in_memory_repo, after_year, yr, num_of_books):
    books = book_services.get_book_ids_by_year(yr, in_memory_repo, after_year)
    books = book_services.get_books(books, in_memory_repo)
    assert len(books) == num_of_books
    if len(books) > 0:
        assert type(books[0]['id']) == int


def test_get_books_by_author(in_memory_repo):
    author = in_memory_repo.get_author(791996)
    assert author.full_name == "Maki Minami"
    book_ids = book_services.get_book_ids_by_author(author, in_memory_repo)
    assert len(book_ids) == 1


@pytest.mark.parametrize(('author_name', 'num_of_books'), (
        ("Maki Minami", 1),
        ("abc", 0)
))
def test_get_books_by_author_name(in_memory_repo, author_name, num_of_books):
    book_ids = book_services.get_book_ids_by_author_name(author_name, in_memory_repo)
    assert len(book_ids) == num_of_books


@pytest.mark.parametrize(('publisher_name', 'num_of_books'), (
        ("Marvel", 1),
        ("abc", 0)
))
def test_get_books_by_publisher_name(in_memory_repo, publisher_name, num_of_books):
    book_ids = book_services.get_book_ids_by_publisher_name(publisher_name, in_memory_repo)
    assert len(book_ids) == num_of_books


def test_get_books_by_title(in_memory_repo):
    book_ids = book_services.get_book_ids_by_title("seiyuu", in_memory_repo)
    assert len(book_ids) == 1
    books = book_services.get_books(book_ids, in_memory_repo)
    assert len(books) == 1
    book = books[0]
    assert book['title'] == "Seiyuu-ka! 12"


# test review services
@pytest.mark.parametrize(('book_id', 'num_of_reviews', 'raises'), (
        (18711343, 3, False),
        (18955715, 4, False),
        (2168737, 1, False),
        (1, 0, True)
))
def test_get_reviews_for_book(in_memory_repo, book_id, num_of_reviews, raises):
    if raises:
        with pytest.raises(book_services.NonExistentBookException):
            reviews = book_services.get_reviews_for_book(book_id, in_memory_repo)
        return
    reviews = book_services.get_reviews_for_book(book_id, in_memory_repo)
    assert len(reviews) == num_of_reviews
    if len(reviews) > 0:
        assert type(reviews[0]['rating']) == int


def test_can_add_review(in_memory_repo):
    book_id = 13340336
    review_text = 'The loonies are stripping the supermarkets bare!'
    user_name = 'jreede0'

    # Call the service layer to add the review.
    book_services.add_review(book_id, 5, review_text, user_name, in_memory_repo)

    # Retrieve the reviews for the book from the repository.
    reviews_as_dict = book_services.get_reviews_for_book(book_id, in_memory_repo)

    # Check that the reviews include a review with the new review text.
    assert next(
        (dictionary['text'] for dictionary in reviews_as_dict if dictionary['text'] == review_text),
        None) is not None


def test_cannot_add_review_for_non_existent_book(in_memory_repo):
    book_id = 1
    review_text = 'The loonies are stripping the supermarkets bare!'
    user_name = 'jreede0'

    # Call the service layer to attempt to add the review.
    with pytest.raises(book_services.NonExistentBookException):
        book_services.add_review(book_id, 3, review_text, user_name, in_memory_repo)


def test_cannot_add_review_by_unknown_user(in_memory_repo):
    book_id = 13340336
    review_text = 'The loonies are stripping the supermarkets bare!'
    user_name = 'not user'

    # Call the service layer to attempt to add the review.
    with pytest.raises(book_services.UnknownUserException):
        book_services.add_review(book_id, 5, review_text, user_name, in_memory_repo)


