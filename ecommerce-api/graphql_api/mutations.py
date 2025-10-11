import strawberry
from .types import Product,ProductInput,ProductUpdateInput,product_to_graphql
from utils.database import SessionLocal,Base
from uuid import UUID,uuid4
from models.product import Products
from models.order import Orders
from typing import Optional
from utils.cache import delete_data
# import redis
# import os
from utils.cache import redis_client
from .types import Order,Orderitem,orders_to_graphql,orderitem_to_graphql,OrderItemInput,CreateOrderInput
from models.order_item import OrderItem

# redis_client = redis.Redis(host=os.getenv('REDIS_HOST','redis'),port=int(os.getenv("REDIS_PORT", 6379)),db=0,decode_responses=True)

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
        
    @strawberry.mutation
    def create_order(self, input: CreateOrderInput) -> Order:
        with SessionLocal() as db:
            # Step 1: Calculate total and validate items
            total_amount = 0.0
            order_items = []
        
            for item in input.items:
                # Step 2: Query product from database
                product = db.query(Products).filter(Products.product_id == UUID(item.product_id)).first()
            
                # Step 3: Validate product exists
                if not product:
                    raise ValueError(f"Product {item.product_id} not found")
                
                #step 3.5: validate sufficient stock
                stock_count = getattr(product, "stock_count", None)
                if stock_count is not None and stock_count < item.quantity:
                    raise ValueError(f"insufficient stock for product {item.product_id}. Available: {stock_count}, Requested: {item.quantity}")            
                
                # Step 4: Validate quantity
                if item.quantity <= 0:
                    raise ValueError("Quantity must be positive")
                # step 4.5: Decrease stock count
                product.stock_count -= item.quantity #type: ignore
            
                # Step 5: Calculate item total
                item_total = product.price * item.quantity
                total_amount += item_total
                
            
                # Step 6: Create OrderItem (you'll need to import OrderItem model)
                order_item = OrderItem(
                    id=uuid4(),
                    product_id=UUID(item.product_id),
                    quantity=item.quantity,
                    price_at_purchase=product.price
                    )
                order_items.append(order_item)

        
            # Step 7: Create the order
            new_order = Orders(
                order_id=uuid4(),
                customer_id=UUID(input.customer_id),
                total_amount=total_amount,
                status="pending"  # Don't forget to set initial status!
                )
        
            # Step 8: Add items to order
            new_order.items = order_items
        
            # Step 9: Save to database
            db.add(new_order)
            db.commit()
            db.refresh(new_order)
            return orders_to_graphql(new_order)







