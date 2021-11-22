import pytest


class TestBookResults:
    def test_single_book_result(self, client):
        response = client.get('/book?id=18955715')
        assert response.status_code == 200

        # title
        assert b'Gray-man' in response.data
        # author
        assert b'Katsura Hoshino' in response.data
        # review
        assert b'2021-06-12' in response.data
        # TODO inventory detail

    def test_book_result_list(self, client):
        response = client.get('/search_books_result?book_ids=17405342,18711343,1')
        assert response.status_code == 200

        # title
        assert b'Seiyuu-ka! 12' in response.data
        # second book
        assert b'Takashi Murakami'

    def test_search_by_title(self, client):

        response = client.get('/process_search_book?method=Title&param=seiyuu')

        assert response.headers['Location'] == 'http://localhost/search_books_result?book_ids=17405342&page=1'

    def test_search_by_author(self, client):
        response = client.get('/process_search_book?method=Author&param=Maki%20Minami')
        assert response.headers['Location'] == 'http://localhost/search_books_result?book_ids=17405342&page=1'

    def test_search_by_publisher(self, client):
        response = client.get('/process_search_book?method=Publisher&param=Hakusensha')
        assert response.headers['Location'] == 'http://localhost/search_books_result?book_ids=17405342&page=1'

    def test_search_by_year(self, client):
        response = client.get('/process_search_book?method=Release Year&param=2013')
        assert response.headers['Location'] == 'http://localhost/search_books_result?book_ids=17405342&page=1'

    def test_search_by_since_year(self, client):
        response = client.get('/process_search_book?method=Year since&param=2011')
        assert response.headers['Location'] == 'http://localhost/search_books_result?book_ids=17405342%2C18711343&page=1'
