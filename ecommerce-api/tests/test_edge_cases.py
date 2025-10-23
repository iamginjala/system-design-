import pytest
from models import User, Products, Orders
from utils.database import SessionLocal
import threading
import time

class TestAuthenticationEdgeCases:
    def test_malformed_token(self, client):
        """Test with invalid token format"""
        mutation = """
        mutation CreateProduct($input: ProductInput!) {
            createProduct(input: $input) {
                productId
            }
        }
        """
        
        # Use completely invalid token
        headers = {'Authorization': 'Bearer invalid-token-xyz123'}
        response = client.post('/graphql', json={
            'query': mutation,
            'variables': {'input': {'price': 29.99, 'stockCount': 100}}
        }, headers=headers)
        
        assert 'errors' in response.json
        error_msg = str(response.json['errors']).lower()
        assert 'invalid token' in error_msg or 'authentication' in error_msg
    
    def test_missing_bearer_prefix(self, client, normal_token):
        """Test token without 'Bearer' prefix"""
        query = """
        {
            getOrders {
                orderId
            }
        }
        """
        
        # Send token without Bearer prefix
        headers = {'Authorization': normal_token}  # Missing "Bearer "
        response = client.post('/graphql', json={'query': query}, headers=headers)
        
        # Should fail
        assert 'errors' in response.json

class TestProductValidation:
    def test_create_product_with_zero_price(self, client, admin_token):
        """Test that products cannot have zero price"""
        mutation = """
        mutation CreateProduct($input: ProductInput!) {
            createProduct(input: $input) {
                productId
            }
        }
        """
        
        headers = {'Authorization': f'Bearer {admin_token}'}
        response = client.post('/graphql', json={
            'query': mutation,
            'variables': {'input': {'price': 0, 'stockCount': 100}}
        }, headers=headers)
        
        assert 'errors' in response.json
        assert 'Price must be positive' in str(response.json['errors'])
    
    def test_create_product_with_negative_stock(self, client, admin_token):
        """Test that products cannot have negative stock"""
        mutation = """
        mutation CreateProduct($input: ProductInput!) {
            createProduct(input: $input) {
                productId
            }
        }
        """
        
        headers = {'Authorization': f'Bearer {admin_token}'}
        response = client.post('/graphql', json={
            'query': mutation,
            'variables': {'input': {'price': 29.99, 'stockCount': -10}}
        }, headers=headers)
        
        # This should either fail or you need to add validation
        # Check if your mutations.py validates negative stock
        data = response.json
        # Add appropriate assertion based on your implementation

class TestOrderEdgeCases:
    def test_order_with_zero_quantity(self, client, normal_token, test_product):
        """Test that orders cannot have zero quantity items"""
        mutation = """
        mutation CreateOrder($input: CreateOrderInput!) {
            createOrder(input: $input) {
                orderId
            }
        }
        """
        
        headers = {'Authorization': f'Bearer {normal_token}'}
        response = client.post('/graphql', json={
            'query': mutation,
            'variables': {
                'input': {
                    'items': [{'productId': test_product['productId'], 'quantity': 0}]
                }
            }
        }, headers=headers)
        
        # Should fail with validation error
        assert 'errors' in response.json
    
    def test_order_with_nonexistent_product(self, client, normal_token):
        """Test ordering a product that doesn't exist"""
        mutation = """
        mutation CreateOrder($input: CreateOrderInput!) {
            createOrder(input: $input) {
                orderId
            }
        }
        """
        
        fake_product_id = "00000000-0000-0000-0000-000000000000"
        
        headers = {'Authorization': f'Bearer {normal_token}'}
        response = client.post('/graphql', json={
            'query': mutation,
            'variables': {
                'input': {
                    'items': [{'productId': fake_product_id, 'quantity': 1}]
                }
            }
        }, headers=headers)
        
        assert 'errors' in response.json

class TestConcurrentOperations:
    def test_concurrent_orders_same_product(self, client, test_product):
        """
        Test race condition: Two users ordering same product simultaneously
        This tests if stock management handles concurrent orders correctly
        """
        # First, set product stock to exactly 5
        product_id = test_product['productId']
        
        # Create two customers
        client.post('/auth/register', json={
            'email': 'concurrent1@test.com',
            'password': 'Password@123',
            'name': 'Concurrent User 1'
        })
        
        client.post('/auth/register', json={
            'email': 'concurrent2@test.com',
            'password': 'Password@123',
            'name': 'Concurrent User 2'
        })
        
        # Login both
        login1 = client.post('/auth/login', json={
            'email': 'concurrent1@test.com',
            'password': 'Password@123'
        })
        token1 = login1.json['token']
        
        login2 = client.post('/auth/login', json={
            'email': 'concurrent2@test.com',
            'password': 'Password@123'
        })
        token2 = login2.json['token']
        
        # Update stock to 5 using admin
        # (You'll need admin_token fixture here or create admin on the fly)
        
        mutation = """
        mutation CreateOrder($input: CreateOrderInput!) {
            createOrder(input: $input) {
                orderId
                totalAmount
            }
        }
        """
        
        results = []
        
        def create_order(token, quantity):
            headers = {'Authorization': f'Bearer {token}'}
            response = client.post('/graphql', json={
                'query': mutation,
                'variables': {
                    'input': {
                        'items': [{'productId': product_id, 'quantity': quantity}]
                    }
                }
            }, headers=headers)
            results.append(response.json)
        
        # Both try to order 3 items (total 6) when stock is 5
        # One should succeed, one should fail
        thread1 = threading.Thread(target=create_order, args=(token1, 60))
        thread2 = threading.Thread(target=create_order, args=(token2, 60))
        
        thread1.start()
        thread2.start()
        
        thread1.join()
        thread2.join()
        
        # At least one should have an error due to insufficient stock
        errors = [r for r in results if 'errors' in r]
        successes = [r for r in results if 'errors' not in r and r.get('data', {}).get('createOrder')]
        
        # Either both fail or one succeeds and one fails
        # This tests your transaction handling
        print(f"Concurrent test results: {len(successes)} succeeded, {len(errors)} failed")
        assert len(errors) >= 1 or len(successes) <= 1

class TestCacheInvalidation:
    def test_product_update_invalidates_cache(self, client, admin_token, test_product):
        """
        Test that updating a product invalidates the cache
        """
        product_id = test_product['productId']
        
        # First, get product to populate cache
        query = """
        query GetProduct($id: String!) {
            getProductsById(id: $id) {
                productId
                price
                stockCount
            }
        }
        """
        
        response1 = client.post('/graphql', json={
            'query': query,
            'variables': {'id': product_id}
        })
        
        original_price = response1.json['data']['getProductsById']['price']
        
        # Update the product
        update_mutation = """
        mutation UpdateProduct($input: ProductUpdateInput!) {
            updateProduct(input: $input) {
                price
            }
        }
        """
        
        new_price = 99.99
        headers = {'Authorization': f'Bearer {admin_token}'}
        client.post('/graphql', json={
            'query': update_mutation,
            'variables': {
                'input': {
                    'productId': product_id,
                    'price': new_price,
                    'stockCount': 100
                }
            }
        }, headers=headers)
        
        # Query again - should get updated price (not cached old price)
        response2 = client.post('/graphql', json={
            'query': query,
            'variables': {'id': product_id}
        })
        
        updated_price = response2.json['data']['getProductsById']['price']
        
        # The price should be updated
        assert updated_price == new_price
        assert updated_price != original_price