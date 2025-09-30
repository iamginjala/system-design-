from utils.database import Base
from sqlalchemy import Column,Float,String,DateTime,ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from .order import Orders
from sqlalchemy.orm import relationship
class Payments(Base):
    __tablename__ = 'payments'
    payment_id = Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey('orders.order_id'),nullable=False,)
    customer_id = Column(String(255),nullable=False,index=True)
    amount = Column(Float(10))
    currency = Column(String,nullable=False,default='INR')
    payment_method = Column(String,nullable=False,default='UPI')
    payment_status = Column(String,default='Pending',nullable=False)
    transaction_id = Column(String,nullable=True)
    created_at = Column(DateTime,default=datetime.utcnow)
    updated_at = Column(DateTime,onupdate=datetime.utcnow)


