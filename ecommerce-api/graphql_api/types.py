from strawberry.flask.views import GraphQLView
import strawberry
import uuid
from typing import Optional
from datetime import datetime
from models.product import Products
from models.order import Orders
from models.order_item import OrderItem

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

@strawberry.input
class ProductInput:
    price: float
    stock_count: int

@strawberry.input
class ProductUpdateInput:
    product_id: str
    stock_count: Optional[int]
    price: Optional[float]

""" types for order and orderitem"""
@strawberry.type
class Orderitem:
    id: str
    product_id: str 
    quantity: int
    price_at_purchase: float
    product: Product

@strawberry.type
class Order:
     order_id: str
     customer_id: str
     total_amount: float
     status: str
     created_at: Optional[datetime] = None
     last_updated: Optional[datetime] = None
     items: list[Orderitem]

def orders_to_graphql(db_orders: Orders) ->  Order:
    return Order(order_id=str(db_orders.order_id), # type: ignore 
                 customer_id=str(db_orders.customer_id), 
                 total_amount= db_orders.total_amount, #type: ignore
                 status=db_orders.status, # type: ignore
                 created_at=db_orders.created_at, #type: ignore
                 last_updated=db_orders.last_updated, #type: ignore
                 items=[orderitem_to_graphql(item) for item in db_orders.items] #type:ignore 
                 )

def orderitem_to_graphql(db_orderitems: OrderItem) -> Orderitem:
    return Orderitem(id= str(db_orderitems.id), #type: ignore
                     product_id=str(db_orderitems.product_id),
                     quantity=db_orderitems.quantity, #type: ignore
                     price_at_purchase=db_orderitems.price_at_purchase, #type: ignore
                     product=product_to_graphql(db_orderitems.product))
