import pytest
from utils.cache import redis_client
import time

class  TestRedisCaching:
    def test_cache_miss_hit_query(self,client,test_product):

        query = """
                {
                   getProducts {
                   productId
                   price
                   }
                }
                """
        cached = redis_client.get("products:all")
        response1 = client.post('/graphql',json={'query':query})
        assert cached is None

        cached = redis_client.get("products:all")
        response2 = client.post('/graphql',json={'query':query})

        assert response1.json == response2.json
        assert cached is not None

    def test_cache_invalidation_on_update(self,admin_token,test_product,client):
        product_id = test_product['productId']
        query = """
                query GetProductsById($productId: String!)
                { getProductsById(id: $productId){
                productId
                price
                stockCount
                }
                }
                """
        vars = {'productId':product_id}
        request = client.post('/graphql',json={'query':query,'variables':vars})
        cached =redis_client.get(product_id)
        assert cached is not None
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
        cached_after = redis_client.get(product_id)
        assert cached_after is None
        request2 = client.post('/graphql',json={'query':query,'variables':vars})
        assert request2.json['data']['getProductsById']['price'] == 39.99
    
    def test_cache_invalidation_on_delete(self,admin_token,test_product,client):
        product_id = test_product['productId']
        query = """
                query GetProductsById($productId: String!)
                { getProductsById(id: $productId){
                productId
                price
                stockCount
                }
                }
                """
        vars = {'productId':product_id}
        request = client.post('/graphql',json={'query':query,'variables':vars})
        cached =redis_client.get(product_id)
        assert cached is not None
        delete_mutation = """
            mutation DeleteProduct($productId: String!) {
                deleteProduct(productId: $productId)
            }
            """
    
        delete_vars = {"productId": product_id}
        headers = {'Authorization': f'Bearer {admin_token}'}
    
        response = client.post('/graphql',
            json={'query': delete_mutation, 'variables': delete_vars},
            headers=headers
        )
        cached_after = redis_client.get(product_id)
        assert cached_after is None
    
    def test_cache_ttl_expiration(self,client,test_product):
        query = """
                {
                  getproducts{
                  productId
                  price
                  }
                  }  
                  """
        time.sleep(61)
        cached = redis_client.get("products:all")
        assert cached is None






        

