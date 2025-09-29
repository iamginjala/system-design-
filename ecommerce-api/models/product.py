from utils.database import Base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column,DATETIME,Integer
from datetime import datetime
import uuid

class Products(Base):
    __tablename__ = 'products'
    product_id = Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4,index=True)
    stock_count = Column(Integer,nullable=False,default=0)
    last_updated = Column(DATETIME,onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<product {self.product_id} count: {self.stock_count}>"
    