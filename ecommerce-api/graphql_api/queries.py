from .types import Product,product_to_graphql
from models.product import Products
from utils.database import SessionLocal
import strawberry
from typing import Optional
from uuid import UUID
from utils.cache import get_data,set_data
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
        cached = get_data(id)
        if isinstance(cached,dict):
            print("cache hit - Retrieved from redis")
            return product_to_graphql(cached) #type: ignore
        else:
            print("Cache miss- Querying from database")
            with SessionLocal() as db:
                try:
                    prod_by_id = db.query(Products).filter(Products.product_id == UUID(id)).first()
                    if prod_by_id:
                        prod_data = {
                            "product_id": id,
                            "stock_count": prod_by_id.stock_count,
                            "price": prod_by_id.price,
                            "last_updated": prod_by_id.last_updated.isoformat() if prod_by_id.last_updated else None  # type: ignore
                        }
                        set_data(id,prod_data)
                        return  product_to_graphql(prod_by_id) 
                    return None
                except ValueError as e:
                    return None




