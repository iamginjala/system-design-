import pytest

class TestCreateProductMutation:
    def test_sucess_with_admin_token(self,client,admin_token):
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

        data = response.json

        assert response.status_code == 200
        assert 'errors' not in data
        assert data['data']['createProduct']['price'] == 29.99

    def test_fails_without_token(self,client):
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
        response = client.post('/graphql',json={'query':mutation,'variables':variables})
        data = response.json

        assert 'errors' in data
        assert 'Authentication required' in str(data['errors'])

    def test_fails_with_normal_token(self,client,normal_token):
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
    
    def test_fails_with_negative_price(self,client,admin_token):
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
                "price":-29.99,
                "stockCount":100,
            }
        }
        headers = {'Authorization': f'Bearer {admin_token}'}
        response = client.post('/graphql',json={'query':mutation,'variables':variables},headers=headers)
        data= response.json

        assert 'errors' in data
        assert 'Price must be positive' in str(data['errors'])

class TestUpdateProductMutation:
    def test_sucess_with_admin_token(self,client,admin_token,test_product):
        product_id = test_product['productId']
        mutation = """
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
                "price": 29.99,
                "stockCount":50,
            }
        }
        headers = {'Authorization':f'Bearer {admin_token}'}
        response = client.post('/graphql',json={'query':mutation,'variables':variables},headers=headers)

        data = response.json
        if 'errors' in data or data['data']['updateProduct'] is None:
            print(f"Update failed: {data}")
    
        assert 'errors' not in data
        assert data['data']['updateProduct'] is not None
        assert data['data']['updateProduct']['price'] == 29.99
        assert response.status_code == 200

    def test_fails_without_token(self,client,test_product):
        product_id = test_product['productId']
        mutation = """
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
                "price": 29.99,
                "stockCount":50,
            }
        }
        response = client.post('/graphql',json={'query':mutation,'variables':variables})
        data = response.json

        assert 'errors' in data
        assert 'Authentication required' in str(data['errors'])

    def test_fails_with_normal_token(self,client,normal_token,test_product):
        product_id = test_product['productId']
        mutation = """
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
                "price": 29.99,
                "stockCount":50,
            }
        }
        headers = {'Authorization' : f'Bearer {normal_token}'}
        response = client.post('/graphql',json={'query':mutation,'variables':variables},headers=headers)
        data = response.json

        assert 'errors' in data
        assert 'Admin access required' in str(data['errors'])
    
    def test_fails_with_negative_price(self,client,admin_token,test_product):
        product_id = test_product['productId']
        mutation = """
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
                "price": -29.99,
                "stockCount":50,
            }
        }
        headers = {'Authorization': f'Bearer {admin_token}'}
        response = client.post('/graphql',json={'query':mutation,'variables':variables},headers=headers)
        data= response.json

        assert 'errors' in data
        assert 'Price must be positive' in str(data['errors'])

class TestDeleteProductMutation:
    def test_sucess_with_admin_token(self,client,admin_token):
        create_mutation = """
                mutation CreateProduct($input: ProductInput!) {
                    createProduct(input: $input) {
                   productId
                      }
                       }
                      """
        create_vars = {"input": {"price": 29.99, "stockCount": 100}}
        headers = {'Authorization': f'Bearer {admin_token}'}
    
        create_response = client.post('/graphql',
            json={'query': create_mutation, 'variables': create_vars},
            headers=headers)
    
        product_id = create_response.json['data']['createProduct']['productId']
        # Now delete it
        delete_mutation = """
            mutation DeleteProduct($productId: String!) {
                deleteProduct(productId: $productId)
            }
            """
    
        delete_vars = {"productId": product_id}
    
        response = client.post('/graphql',
            json={'query': delete_mutation, 'variables': delete_vars},
            headers=headers
        )
    
        data = response.json
        assert 'errors' not in data
        assert data['data']['deleteProduct'] == True
    def test_fails_without_token(self,client):
        create_mutation = """
                mutation CreateProduct($input: ProductInput!) {
                    createProduct(input: $input) {
                   productId
                      }
                       }
                      """
        create_vars = {"input": {"price": 29.99, "stockCount": 100}}
       
        response = client.post('/graphql',json={'query':create_mutation,'variables':create_vars})
        data = response.json

        assert 'errors' in data
        assert 'Authentication required' in str(data['errors'])

    def test_fails_with_normal_token(self,client,normal_token):
        create_mutation = """
                mutation CreateProduct($input: ProductInput!) {
                    createProduct(input: $input) {
                   productId
                      }
                       }
                      """
        create_vars = {"input": {"price": 29.99, "stockCount": 100}}
        headers = {'Authorization' : f'Bearer {normal_token}'}
        response = client.post('/graphql',json={'query':create_mutation,'variables':create_vars},headers=headers)
        data = response.json

        assert 'errors' in data
        assert 'Admin access required' in str(data['errors'])
    def test_fails_for_non_productid(self,client,admin_token):
        create_mutation = """
                mutation CreateProduct($input: ProductInput!) {
                    createProduct(input: $input) {
                   productId
                      }
                       }
                      """
        create_vars = {"input": {"price": 29.99, "stockCount": 100}}
        headers = {'Authorization': f'Bearer {admin_token}'}
    
        create_response = client.post('/graphql',
            json={'query': create_mutation, 'variables': create_vars},
            headers=headers)
    
        product_id = "123456"
        # Now delete it
        delete_mutation = """
            mutation DeleteProduct($productId: String!) {
                deleteProduct(productId: $productId)
            }
            """
    
        delete_vars = {"productId": product_id}
    
        response = client.post('/graphql',
            json={'query': delete_mutation, 'variables': delete_vars},
            headers=headers
        )
    
        data = response.json
        assert 'errors' in data

class TestCreateOrderMutation:
    def test_create_order_normal(self, client, normal_token, test_product):
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

        headers = {'Authorization': f'Bearer {normal_token}'}
        response = client.post('/graphql',
            json={'query': mutation, 'variables': variables},
            headers=headers
        )

        data = response.json
        assert 'errors' not in data
        assert data['data']['createOrder']['status'] == 'pending'
        # The total should be 2 * 29.99 = 59.98
        assert data['data']['createOrder']['totalAmount'] == 59.98

    def test_create_order_admin(self,client,admin_token,test_product):
        product_id =  test_product['productId']
        mutation = """
        mutation CreateOrder($input: CreateOrderInput!) {
            createOrder(input: $input) {
                orderId
                totalAmount
                status}}"""

        variables = {
            "input": {
                "items": [
                    {
                        "productId": product_id,
                        "quantity": 4
                    }
                ]
            }
        }
        headers = {'Authorization': f'Bearer {admin_token}'}
        response = client.post('/graphql',json={'query':mutation,'variables':variables},headers=headers)

        data = response.json

        assert 'errors' not in data
        assert data['data']['createOrder']['status'] == 'pending'
        assert data['data']['createOrder']['totalAmount'] == 119.96

    def test_fails_without_token(self,client,test_product):
        product_id =  test_product['productId']
        mutation = """
        mutation CreateOrder($input: CreateOrderInput!) {
            createOrder(input: $input) {
                orderId
                totalAmount
                status}}"""

        variables = {
            "input": {
                "items": [
                    {
                        "productId": product_id,
                        "quantity": 4
                    }
                ]
            }
        }
        response = client.post('/graphql',json={'query':mutation,'variables':variables})

        data = response.json

        assert 'errors' in data
        assert 'Authentication required' in str(data['errors'])
    
    def test_fails_with_invalid_product_id(self,client,normal_token):
        product_id =  "12567"
        mutation = """
        mutation CreateOrder($input: CreateOrderInput!) {
            createOrder(input: $input) {
                orderId
                totalAmount
                status}}"""

        variables = {
            "input": {
                "items": [
                    {
                        "productId": product_id,
                        "quantity": 4
                    }
                ]
            }
        }
        headers = {'Authorization': f'Bearer {normal_token}'}
        response = client.post('/graphql',json={'query':mutation,'variables':variables},headers=headers)

        data = response.json

        assert 'errors' in data

    def test_fails_with_insufficient_stock(self,client,admin_token,test_product):
        product_id = test_product['productId']
        mutation = """
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
                "productId":product_id,
                "price": 29.99,
                "stockCount":0,
            }
        }
        headers = {'Authorization':f'Bearer {admin_token}'}
        response = client.post('/graphql',json={'query':mutation,'variables':variables},headers=headers)
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

        headers = {'Authorization': f'Bearer {admin_token}'}
        response = client.post('/graphql',
            json={'query': mutation, 'variables': variables},
            headers=headers
        )

        data = response.json
        assert 'errors' in data




