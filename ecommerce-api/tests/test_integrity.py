import pytest
from models import Orders, OrderItem, Products
from utils.database import SessionLocal
from uuid import UUID

class TestDataIntegrity:
    def test_customers_sees_only_own_orders(self,normal_token,test_product,client,normal_user):
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
                "items": [
                    {
                        "productId": product_id,
                        "quantity": 2
                    }
                ]
            }
        }

        headers = {'Authorization': f'Bearer {normal_token}'}
        response1 = client.post('/graphql',
            json={'query': mutation, 'variables': variables},
            headers=headers
        )
        customer_id = normal_user['user_id']
        query = """
                    {
            getOrders {
                orderId
                customerId
                          }
                         }
                  """
        response = client.post('/graphql', json={'query': query}, headers=headers) 
        orders = response.json['data']['getOrders']
        assert len(orders) >= 1

        for order in orders:
            assert order['customerId'] == customer_id

    
    def test_admins_can_see_all_orders(self,normal_token,admin_user,client,test_product,admin_token,normal_user):
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
                "items": [
                    {
                        "productId": product_id,
                        "quantity": 2
                    }
                ]
            }
        }

        headers = {'Authorization': f'Bearer {normal_token}'}
        response1 = client.post('/graphql',
            json={'query': mutation, 'variables': variables},
            headers=headers
        )
        headers_admin = {'Authorization': f'Bearer {admin_token}'}
        client.post('/graphql',
        json={'query': mutation, 'variables': variables},
        headers=headers_admin
    )
        query = """
                    {
            getOrders {
                orderId
                customerId
                          }
                         }
                  """
        response = client.post('/graphql', json={'query': query}, headers=headers) 
        orders = response.json['data']['getOrders']
        assert len(orders) >= 2
        customer_ids = [order['customerId'] for order in orders]
        assert admin_user['user_id'] in customer_ids
        assert normal_user['user_id'] in customer_ids

    def test_order_items_link_to_products(self, client, normal_token, test_product):
        # Create an order with items
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
                "items": [
                    {
                        "productId": product_id,
                        "quantity": 2
                    }
                ]
            }
        }
        
        headers = {'Authorization': f'Bearer {normal_token}'}
        response = client.post('/graphql',
            json={'query': mutation, 'variables': variables},
            headers=headers
        )
        
        order_id = response.json['data']['createOrder']['orderId']
        
        # Query database
        db = SessionLocal()
        order = db.query(Orders).filter(Orders.order_id == UUID(order_id)).first()
        db.close()
        
        # Assertions:
        assert len(order.items) > 0  # type: ignore
        
        for item in order.items:    #type: ignore
            # Each item should reference a real product
            db = SessionLocal()
            product = db.query(Products).filter(Products.product_id == item.product_id).first()
            db.close()
            
        assert product is not None  # Product exists
        assert item.product_id == UUID(product_id)  # Correct product