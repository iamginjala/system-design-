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
    product_id : str = strawberry.field(description="unique product identifier (UUID format)")
    stock_count : int = strawberry.field(description="Current available inventory count")
    price : float = strawberry.field(description="Product Price in INR")
    last_updated: Optional[datetime] = strawberry.field(default=None,description="Timestamp of last product update")

def product_to_graphql(db_product: Products) -> Product:
    return Product(
        product_id=str(db_product.product_id), # type: ignore
        stock_count=db_product.stock_count, # type: ignore
        price= db_product.price, # type: ignore
        last_updated= db_product.last_updated # type: ignore
    )

@strawberry.input
class ProductInput:
    price: float = strawberry.field(description="Input Product Price in INR")
    stock_count: int = strawberry.field(description="Input Inventory count")

@strawberry.input
class ProductUpdateInput:
    product_id: str = strawberry.field(description="unique product identifier (UUID format)")
    stock_count: Optional[int] = strawberry.field(description="Update Inventory count")
    price: Optional[float] = strawberry.field(description="Update Product Price in INR")

""" types for order and orderitem"""
@strawberry.type
class Orderitem:
    id: str = strawberry.field(description="unique order identifier (UUID format)")
    product_id: str = strawberry.field(description="unique product identifier (UUID format) links to product_id in product model")
    quantity: int = strawberry.field(description="how many products placed")
    price_at_purchase: float = strawberry.field(description="Product Price at the time of purchase in INR(immutable)")
    product: Product =strawberry.field(description="links to product type class")

@strawberry.type
class Order:
     order_id: str = strawberry.field(description="unique order identifier (UUID format)")
     customer_id: str = strawberry.field(description="unique customer identifier (UUID format)")
     total_amount: float = strawberry.field(description="total amount placed for the order(immutable)")
     status: str = strawberry.field(description="status of the order")
     created_at: Optional[datetime] = strawberry.field(default=None,description="Timestamp of last order created")
     last_updated: Optional[datetime] = strawberry.field(default=None,description="Timestamp of last order update")
     items: list[Orderitem] = strawberry.field(description="links to the list of orderitem type class")

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

@strawberry.input
class OrderItemInput:
    product_id: str =  strawberry.field(description="unique product identifier (UUID format)")
    quantity: int = strawberry.field(description="how many products placed")

@strawberry.input
class CreateOrderInput:
    items: list[OrderItemInput] = strawberry.field(description="links to the list of orderiteminput type class")
