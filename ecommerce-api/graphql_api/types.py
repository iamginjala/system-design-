from strawberry.flask.views import GraphQLView
import strawberry
import uuid
from typing import Optional
from datetime import datetime
from models.product import Products

@strawberry.type
class Product:
    product_id : str
    stock_count : int
    price : float
    last_updated: Optional[datetime] = None

def product_to_graphql(db_product: Products) -> Product:
    return Product(
        product_id=str(db_product.product_id),
        stock_count=db_product.stock_count, # type: ignore
        price= db_product.price, # type: ignore
        last_updated= db_product.last_updated # type: ignore
    )


