import pytest

import library.adapters.repository_populate
from library import create_app
from library.adapters import memory_repository
from library.adapters.memory_repository import MemoryRepository
from utils import get_project_root

# the csv files in the test folder are different from the csv files in the library/adapters/data folder!
# tests are written against the csv files in tests, this data path is used to override default path for testing
TEST_DATA_PATH = get_project_root() / "tests" / "data"


@pytest.fixture
def in_memory_repo():
    repo = MemoryRepository()
    library.adapters.repository_populate.populate(TEST_DATA_PATH, repo)
    return repo


@pytest.fixture
def client():
    my_app = create_app({
        'TESTING': True,  # Set to True during testing.
        'TEST_DATA_PATH': TEST_DATA_PATH,  # Path for loading test data into the repository.
        'WTF_CSRF_ENABLED': False,  # test_client will not send a CSRF token, so disable validation.
        'REPOSITORY': 'memory'
    })

    return my_app.test_client()


class AuthenticationManager:
    def __init__(self, client):
        self.__client = client

    # noinspection SpellCheckingInspection
    def login(self, user_name='jreede0', password='Gk8thq'):
        return self.__client.post(
            'authentication/login',
            data={'user_name': user_name, 'password': password}
        )

    def logout(self):
        return self.__client.get('/auth/logout')


@pytest.fixture
def auth(client):
    return AuthenticationManager(client)
