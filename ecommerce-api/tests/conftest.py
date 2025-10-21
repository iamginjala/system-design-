import pytest
import sys
import os

sys.path.insert(0,os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))

from app import create_app
from utils.database import SessionLocal
from models import User

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


@pytest.fixture
def admin_user(client):
    request = client.post('/auth/register',json={
        'email':'admin@test.com',
        'password':'Admin@123',
        'name': 'admin user'
    })
    db = SessionLocal()
    user = db.query(User).filter(User.email=='admin@test.com').first()
    user.role = 'admin' #type: ignore
    db.commit()
    db.close()

    return user

@pytest.fixture
def normal_user(client):
    request = client.post('/auth/register',json={
        'email':'user@test.com',
        'password':'User@123',
        'name': 'normal user'
    })

    return request.json

@pytest.fixture
def admin_token(client,admin_user):
    request = client.post('/auth/login',json={
        'email':'admin@test.com',
        'password':'Admin@123'
    })
    data = request.json
    token = data['token']

    return token

@pytest.fixture
def normal_token(client,normal_user):
     request = client.post('/auth/login',json={
        'email':'user@test.com',
        'password':'User@123',
    })
     data = request.json
     token = data['token']

     return token
@pytest.fixture(autouse=True)
def cleanup_database():
    """Clean up test users before each test"""
    db = SessionLocal()
    # Delete test users
    db.query(User).filter(User.email.in_(['admin@test.com', 'user@test.com'])).delete(synchronize_session=False)
    db.commit()
    db.close()
    
    yield  # Test runs here
    
    # Cleanup after test too
    db = SessionLocal()
    db.query(User).filter(User.email.in_(['admin@test.com', 'user@test.com'])).delete(synchronize_session=False)
    db.commit()
    db.close()

@pytest.fixture
def test_product(client,admin_token):
        mutation = """
                    mutation CreateProduct($input: ProductInput!)
                    {
                    createProduct(input: $input){
                    productId
                    price
                    stockCount
                    }
                    }
                 """
        variables = {
            "input":{
                "price":29.99,
                "stockCount":100,
            }
        }
        headers = {'Authorization':f'Bearer {admin_token}'}
        response = client.post('/graphql',json={'query':mutation,'variables':variables},headers=headers)

        return response.json['data']['createProduct']