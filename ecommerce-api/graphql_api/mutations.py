import strawberry
from .types import Product,ProductInput,ProductUpdateInput,product_to_graphql
from utils.database import SessionLocal,Base
import uuid
from sqlalchemy.exc import DatabaseError
from flask import jsonify
from models.product import Products
from typing import Optional


@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_product(self,input: ProductInput) ->Product :
        new_product = Products(
            product_id=uuid.uuid4(),
            price=input.price,
            stock_count=input.stock_count
        )
        with SessionLocal() as db:
             db.add(new_product)
             db.commit()
             db.refresh(new_product)
        return product_to_graphql(new_product)

    @strawberry.mutation
    def update_product(self,input: ProductUpdateInput) -> Optional[Product]:
        with SessionLocal() as db:
         new_update = db.query(Products).filter(Products.product_id == input.product_id).first()
         if not new_update:
            return None
         if input.price is not None:
             new_update.price = input.price #type: ignore
         if input.stock_count is not None:
             new_update.stock_count = input.stock_count #type: ignore
            
        db.commit()
        db.refresh(new_update)
        return product_to_graphql(new_update)

    
             
             






