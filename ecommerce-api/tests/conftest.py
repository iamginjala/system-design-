import pytest
import sys
import os

sys.path.insert(0,os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))

from app import create_app

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SECRET_KEY': 'test-secret-key-for-jwt',
        'JWT_EXPIRATION_HOURS':24
    })

    return app

@pytest.fixture
def client(app):
    return app.test_client()