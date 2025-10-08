from utils.database import Base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column,Integer,Float,ForeignKey,Table
import uuid
from .order import Orders
from .product import Products
from sqlalchemy.orm import relationship




class OrderItem(Base):
    __tablename__ = 'order_items'
    id =  Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True),ForeignKey(Orders.order_id),nullable=False)
    product_id = Column(UUID(as_uuid=True),ForeignKey(Products.product_id),nullable=False)
    quantity = Column(Integer,nullable=False)
    price_at_purchase = Column(Float(10),nullable=False)
    
    order = relationship('Orders',back_populates='items')
    product = relationship('Products',back_populates='order_items')
