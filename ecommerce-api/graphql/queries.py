from .types import Product,product_to_graphql
from models.product import Products
from utils.database import SessionLocal
import strawberry
from typing import Optional
from uuid import UUID

@strawberry.type 
class Query:
    @strawberry.field
    def get_products(self) -> list[Product]:
        with SessionLocal() as db:
            prods = db.query(Products).all()

            return [
                product_to_graphql(prod)
                for prod in prods
            ]
    @strawberry.field
    def get_products_by_id(self,id: str) -> Optional[Product]:
        with SessionLocal() as db:
            try:
                prod_by_id = db.query(Products).filter(Products.product_id == UUID(id)).first()
                if prod_by_id:
                    return  product_to_graphql(prod_by_id) 
                return None
            except ValueError as e:
                return None




