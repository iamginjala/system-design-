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



