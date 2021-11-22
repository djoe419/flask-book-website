import pytest

from flask import session

def test_add_review(client, auth):
    # Login a user.
    auth.login()

    # Check that we can retrieve the review page.
    response = client.get('/book?id=17405342')

    response = client.post(
        '/book/review',
        data={'book_id': 17405342, 'rating': 2, 'review': 'book is book'}
    )
    assert response.headers['Location'] == 'http://localhost/book?id=17405342'


@pytest.mark.parametrize(('review', 'messages'), (
        ('Hey', (b'Your comment is too short')),
        ('Who thinks Trump is a f***wit?', (b'Your comment must not contain profanity')),
        ('ass', (b'Your comment is too short',b'Your comment must not contain profanity')),
))
def test_review_with_invalid_input(client, auth, review, messages):
    # Login a user.
    auth.login()

    # Attempt to comment on an article.
    response = client.post(
        '/book/review',
        data={'book_id': 17405342, 'rating': 2, 'review': review}
    )
    # Check that supplying invalid comment text generates appropriate error messages.
    for review in messages:
        assert review in response.data

