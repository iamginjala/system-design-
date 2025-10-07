import strawberry
from .types import Product,ProductInput,ProductUpdateInput,product_to_graphql
from utils.database import SessionLocal,Base
from uuid import UUID,uuid4
from models.product import Products
from typing import Optional
from utils.cache import delete_data
import redis
import os

redis_client = redis.Redis(host=os.getenv('REDIS_HOST','redis'),port=int(os.getenv("REDIS_PORT", 6379)),db=0,decode_responses=True)

@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_product(self,input: ProductInput) ->Product :
        if input.price <= 0:
            raise ValueError("Price must be positive")
        if input.stock_count < 0:
            raise ValueError("Stock cannot be negative")
        new_product = Products(
            product_id=uuid4(),
            price=input.price,
            stock_count=input.stock_count
        )
        with SessionLocal() as db:
            db.add(new_product)
            db.commit()
            db.refresh(new_product)
            redis_client.delete("products:all")
            return product_to_graphql(new_product)

    @strawberry.mutation
    def update_product(self,input: ProductUpdateInput) -> Optional[Product]:
        with SessionLocal() as db:
            new_update = db.query(Products).filter(Products.product_id == UUID(input.product_id)).first()
            if not new_update:
                return None
            
            
            if input.price is not None:
                if input.price <= 0:
                    raise ValueError("Price must be positive")
                new_update.price = input.price #type: ignore
            if input.stock_count is not None:
                if input.stock_count < 0:
                    raise ValueError("Stock cannot be negative")
                new_update.stock_count = input.stock_count #type: ignore

            db.commit()
            db.refresh(new_update)
            delete_data(input.product_id)
            redis_client.delete("products:all")
            return product_to_graphql(new_update)

    @strawberry.mutation
    def delete_product(self,product_id : str) -> bool:
        with SessionLocal() as db:
            delete_product = db.query(Products).filter(Products.product_id == UUID(product_id)).first()

            if not delete_product:
                return False
            db.delete(delete_product)
            db.commit()
            delete_data(product_id)
            redis_client.delete("products:all")

            return True
             
             






