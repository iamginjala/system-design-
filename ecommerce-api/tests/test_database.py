import pytest
from utils.database import SessionLocal
from models import User,Products
from uuid import UUID

class TestDatabaseOperations:
    def test_create_user_in_database(self,client):
        request = client.post('/auth/register',json={'email':'user1@gmail.com',
                                                     'password':'Test@1234',
                                                     'name':'testuser'})
        
        print(f"Response: {request.json}")
        assert request.json['status'] == True
        assert request.status_code == 201
        db = SessionLocal()
        user = db.query(User).filter(User.email == 'user1@gmail.com').first()
        db.close()

        assert user is not None
        assert user.name == 'testuser' # type: ignore
        assert user.role == 'customer' # type: ignore
    def test_duplicate_email_constraint(self,client):
        request1 = client.post('/auth/register',json={'email':'user2@gmail.com',
                                                     'password':'Test@1234',
                                                     'name':'testuser2'})
        request2 = client.post('/auth/register',json={'email':'user2@gmail.com',
                                                     'password':'Test@1234',
                                                     'name':'seconduser'})

        assert request1.status_code == 201
        assert request1.json['status'] == True
        

        assert request2.status_code == 409
        assert request2.json['status'] == False
        assert 'Already have an account' in request2.json['message']
    def test_create_order_links_to_user(self, client, test_product, normal_token, normal_user):
        product_id = test_product['productId']
        mutation = """
            mutation CreateOrder($input: CreateOrderInput!) {
                createOrder(input: $input) {
                    orderId
                    customerId
                    totalAmount
                    status
                }
            }
        """

        variables = {
            "input": {
                "items": [{
                    "productId": product_id,
                    "quantity": 2
                }]
            }
        }

        headers = {'Authorization': f'Bearer {normal_token}'}
        response = client.post('/graphql',
            json={'query': mutation, 'variables': variables},
            headers=headers
        )

        data = response.json
        assert 'errors' not in data
        
        customer_id = data['data']['createOrder']['customerId']
        
        db = SessionLocal()
        user = db.query(User).filter(User.email == normal_user['email']).first()
        db.close()
        
        assert customer_id == str(user.user_id)  # type: ignore

    def test_product_stock_decreases_on_order(self, client, test_product, normal_token):
        from uuid import UUID
    
        product_id = test_product['productId']
        initial_stock = test_product['stockCount']  # Should be 100
    
        mutation = """
        mutation CreateOrder($input: CreateOrderInput!) {
            createOrder(input: $input) {
                orderId
            }
        }
            """

        variables = {
            "input": {
            "items": [{
                "productId": product_id,
                "quantity": 2
                    }]
                }
            }

        headers = {'Authorization': f'Bearer {normal_token}'}
        response = client.post('/graphql',
        json={'query': mutation, 'variables': variables},
        headers=headers
                    )

        data = response.json
        assert 'errors' not in data
    
    # Query database to check stock decreased
        db = SessionLocal()
        product = db.query(Products).filter(Products.product_id == UUID(product_id)).first()
        db.close()
    
        assert product.stock_count == initial_stock - 2  #type: ignore