import strawberry
from .types import Product,ProductInput,ProductUpdateInput,product_to_graphql
from utils.database import SessionLocal,Base
import uuid
from sqlalchemy.exc import DatabaseError
from flask import jsonify
from models.product import Products


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
        




