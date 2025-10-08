from utils.database import Base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column,DateTime,Integer,Float
from datetime import datetime
import uuid
from sqlalchemy.orm import relationship


class Products(Base):
    __tablename__ = 'products'
    product_id = Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4,index=True)
    stock_count = Column(Integer,nullable=False,default=0)
    last_updated = Column(DateTime,default=datetime.utcnow,onupdate=datetime.utcnow)
    price  = Column(Float(10))
    order_items = relationship('OrderItem',back_populates='product')

    def __repr__(self):
        return f"<product {self.product_id} count: {self.stock_count}>"
    