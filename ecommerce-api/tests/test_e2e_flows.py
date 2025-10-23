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
    
class TestAdminWorkflow:
    def test_complete_admin_flow(self,client):
        request = client.post('/auth/register',json={
                'email':'admin@test.com',
                'password':'Admin@123',
                'name': 'admin user'})
        db = SessionLocal()
        user = db.query(User).filter(User.email=='admin@test.com').first()
        user.role = 'admin' #type: ignore
        db.commit()
        admin_customer_id = str(user.user_id),   # type: ignore
        db.close()

        response = client.post('/auth/login',json={
            'email':'admin@test.com'
            ,'password':'Admin@123'
        })
        data = response.json
        admin_token = data['token']
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
        response2 = client.post('/graphql',json={'query':mutation,'variables':variables},headers=headers)
        data = response2.json

        assert response2.status_code == 200
        assert 'errors' not in data
        assert data['data']['createProduct']['price'] == 29.99
        mutation2 = """
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
                "price":19.99,
                "stockCount":100,
            }
        }
        response3 = client.post('/graphql',json={'query':mutation,'variables':variables},headers=headers)
        data = response3.json
        assert response3.status_code == 200
        assert 'errors' not in data
        assert data['data']['createProduct']['price'] == 19.99

        product_id = response2.json['data']['createProduct']['productId']
        assert product_id is not None

        update_mutation =  """
                    mutation UpdateProduct($input: ProductUpdateInput!)
                    {
                    updateProduct(input: $input){
                    productId
                    price
                    stockCount
                    }
                    }
                 """
        variables = {
            "input":{
                "productId": product_id,
                "price": 24.99,
                "stockCount":50,
            }
        }
        update_response = client.post('/graphql',json={'query':update_mutation,'variables':variables},headers=headers)

        data = update_response.json
        if 'errors' in data or data['data']['updateProduct'] is None:
            print(f"Update failed: {data}")
    
        assert 'errors' not in data
        assert data['data']['updateProduct'] is not None
        assert data['data']['updateProduct']['price'] == 24.99
        assert response.status_code == 200

        query = """
                    {
            getOrders {
                orderId
                customerId
                          }
                         }
                  """
        order_response = client.post('/graphql',json={'query':query},headers=headers)

        assert 'errors' not in order_response.json
        delete_mutation = """
        mutation DeleteProduct($productId: String!) {
            deleteProduct(productId: $productId)
        }
        """
        
        delete_response = client.post('/graphql', json={
            'query': delete_mutation,
            'variables': {'productId': product_id}
        }, headers=headers)
        
        assert delete_response.json['data']['deleteProduct'] == True

class TestAuthorizationBoundaries:
    def test_customer_see_only_own_orders(self,client):
        # Register customer A
        reg_a = client.post('/auth/register', json={
            'email': 'customera@test.com',
            'password': 'Password@123',
            'name': 'Customer A'
        })
        print(f"Register A response: {reg_a.json}")

        loginA = client.post('/auth/login', json={
            'email': 'customera@test.com',
            'password': 'Password@123'
        })
        print(f"Login A response: {loginA.json}")
        data_A = loginA.json

        # Check if login was successful
        if 'token' not in data_A:
            print(f"Login A failed: {data_A}")
            assert False, f"Login failed for customer A: {data_A}"

        tokenA = data_A['token']
        
        # Create customer B
        reg_b = client.post('/auth/register', json={
            'email': 'customerb@test.com',
            'password': 'Password@123',
            'name': 'Customer B'
        })
        print(f"Register B response: {reg_b.json}")

        loginB = client.post('/auth/login', json={
            'email': 'customerb@test.com',
            'password': 'Password@123'
        })
        print(f"Login B response: {loginB.json}")
        data_B = loginB.json

        # Check if login was successful
        if 'token' not in data_B:
            print(f"Login B failed: {data_B}")
            assert False, f"Login failed for customer B: {data_B}"

        tokenB = data_B['token']

        db = SessionLocal()
        userA = db.query(User).filter(User.email == 'customera@test.com').first()
        userB = db.query(User).filter(User.email == 'customerb@test.com').first()
        customerA_id = str(userA.user_id)  # type: ignore
        customerB_id = str(userB.user_id) # type: ignore
        db.close()
        query = """
        {
            getOrders {
                orderId
                customerId
            }
        }
        """
        headersA = {'Authorization': f'Bearer {tokenA}'}
        ordersA = client.post('/graphql', json={'query': query}, headers=headersA)
        
        # Customer B queries their orders
        headersB = {'Authorization': f'Bearer {tokenB}'}
        ordersB = client.post('/graphql', json={'query': query}, headers=headersB)

        # Verify A only sees A's orders
        for order in ordersA.json['data']['getOrders']:
            assert order['customerId'] == customerA_id
        
        # Verify B only sees B's orders
        for order in ordersB.json['data']['getOrders']:
            assert order['customerId'] == customerB_id
    
    def test_customer_cannot_create_product(self,client,normal_token):
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
        headers = {'Authorization' : f'Bearer {normal_token}'}
        response = client.post('/graphql',json={'query':mutation,'variables':variables},headers=headers)
        data = response.json

        assert 'errors' in data
        assert 'Admin access required' in str(data['errors'])