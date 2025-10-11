from .types import Product,product_to_graphql
from .types import Order,orders_to_graphql
from models.product import Products
from models.order import Orders 
from utils.database import SessionLocal
import strawberry
from typing import Optional
from uuid import UUID
from utils.cache import get_data,set_data
from utils.cache import redis_client
import json
from datetime import datetime 




@strawberry.type 
class Query:
    @strawberry.field
    def get_products(self) -> list[Product]:
        cached_data = redis_client.get("products:all")
        if cached_data is None:
            print("Cache miss: querying from database")
            with SessionLocal() as db:
                result  = db.query(Products).all()
                res_dict = [
                    {
                        "product_id": str(r.product_id),
                        "stock_count": r.stock_count,
                        "price": r.price,
                        "last_updated": r.last_updated.isoformat() if r.last_updated else None  # type: ignore
                    } for r in result
                ]
                if res_dict:  # Only cache if there's data
                    redis_client.setex("products:all", 60, json.dumps(res_dict))
                return [product_to_graphql(prod) for prod in result]
        else:
            print("cache hit: retrieved from redis")
            res = json.loads(cached_data)  # type: ignore
            return [Product(
                product_id=r["product_id"],
                stock_count=r["stock_count"],
                price=r["price"],
                last_updated=datetime.fromisoformat(r["last_updated"]) if r.get("last_updated") else None
            ) for r in res] 
    @strawberry.field
    def get_products_by_id(self,id: str) -> Optional[Product]:
        cached = get_data(id)
        if isinstance(cached,dict):
            print("cache hit - Retrieved from redis")
            return Product(
                product_id=cached["product_id"],
                stock_count=cached["stock_count"],
                price=cached["price"],
                last_updated=datetime.fromisoformat(cached["last_updated"]) if cached.get("last_updated") else None
            )
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
    @strawberry.field
    def get_orders(self) -> list[Order]:
        with SessionLocal() as db:
            result = db.query(Orders).all()
            return [orders_to_graphql(order) for order in result]
    @strawberry.field
    def get_order_by_id(self,order_id:str) -> Optional[Order]:
        with SessionLocal() as db:
            result = db.query(Orders).filter(Orders.order_id == UUID(order_id)).first()

            if result:
                return orders_to_graphql(result)
            return None





