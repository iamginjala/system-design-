import pytest
from models import User,Products,Orders
from utils.cache import redis_client
from utils.database import SessionLocal

class TestCustomerJourney:
    def test_customer_flow(self,client,test_product):
        request = client.post('/auth/register', json={
            'email':'harsha@gmail.com',
            'password':'Qawsed@1234',
            'name': 'Harsha'
        })


        response = client.post('/auth/login',json={
            'email':'harsha@gmail.com',
            'password':'Qawsed@1234'
        })
        data = response.json
        token = data['token']
        db = SessionLocal()
        user = db.query(User).filter(User.email == 'harsha@gmail.com').first()
        customer_id = str(user.user_id) # type: ignore
        db.close()
        query = """{
                getProducts{
                productId
                price
                }
                }  
                """
        headers = {'Authorization': f'Bearer {token}'}

        client.post('/graphql',json={'query':query})

        cached = redis_client.get('products:all')

        assert cached is not None

        product_id = test_product['productId']
        mutation = """
        mutation CreateOrder($input: CreateOrderInput!) {
            createOrder(input: $input) {
                orderId
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

        create_order = client.post('/graphql',json={'query':mutation,'variables':variables},headers=headers)
        data = create_order.json

        assert 'errors' not in data
        assert data['data']['createOrder']['status'] == 'pending'
        assert data['data']['createOrder']['totalAmount'] == 59.98

        query = """
                    {
            getOrders {
                orderId
                customerId
                          }
                         }
                  """
        ord_status = client.post('/graphql',json={'query':query},headers=headers)
        orders = ord_status.json['data']['getOrders']
        assert len(orders) >= 1

        for order in orders:
            assert order['customerId'] == customer_id
    
    def test_get_product_by_id_with_cache(self, client, test_product):
        """Test getting product by ID - cache miss then cache hit"""
        product_id = test_product['productId']
    
        query = """
                query GetProduct($id: String!) {
                    getProductsById(id: $id) {
                        productId
                        price
                        stockCount
                }
                }
                """
    
    # First call - cache miss
        response1 = client.post('/graphql', json={
            'query': query,
            'variables': {'id': product_id}
        })
    
        data1 = response1.json
        assert 'errors' not in data1
        assert data1['data']['getProductsById']['productId'] == product_id
    
    # Second call - should hit cache
        response2 = client.post('/graphql', json={
            'query': query,
            'variables': {'id': product_id}
        })
    
        data2 = response2.json
        assert data2['data']['getProductsById']['productId'] == product_id

    def test_get_order_by_id(self, client, normal_token, test_product):
        """Test getting order by ID"""
        # First create an order
        product_id = test_product['productId']
    
        create_mutation = """
            mutation CreateOrder($input: CreateOrderInput!) {
            createOrder(input: $input) {
                orderId
            }
            }
            """
    
        headers = {'Authorization': f'Bearer {normal_token}'}
        create_response = client.post('/graphql', json={
            'query': create_mutation,
            'variables': {
                'input': {
                'items': [{'productId': product_id, 'quantity': 1}]
                }
                }
                }, headers=headers)
    
        order_id = create_response.json['data']['createOrder']['orderId']
    
        # Now query that specific order
        query = """
        query GetOrder($orderId: String!) {
        getOrderById(orderId: $orderId) {
            orderId
            totalAmount
            status
        }
        }
        """
    
        response = client.post('/graphql', json={
            'query': query,
            'variables': {'orderId': order_id}
        })
    
        data = response.json
        assert 'errors' not in data
        assert data['data']['getOrderById']['orderId'] == order_id
    
