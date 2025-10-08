from utils.database import Base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column,String,DateTime,Integer,Float
from datetime import datetime
import uuid
from sqlalchemy.orm import relationship

class Orders(Base):
    __tablename__ = 'orders'
    order_id = Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    customer_id = Column(String(255),nullable=False,index=True)
    total_amount = Column(Float(10),nullable=False)
    # quantity = Column(Integer,nullable=False)
    status = Column(String(50),nullable=False,default='pending')
    tracking_info = Column(String,nullable=True)
    created_at = Column(DateTime,nullable=False,default=datetime.utcnow)
    last_updated = Column(DateTime,default=datetime.utcnow,onupdate=datetime.utcnow)
    items = relationship('OrderItem',back_populates='order')

    def __repr__(self):
        return f"<Order {self.order_id}: {self.status}>"
    