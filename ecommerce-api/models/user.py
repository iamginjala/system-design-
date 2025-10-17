from utils.database import Base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column,DateTime,String
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from werkzeug.security import generate_password_hash, check_password_hash


class User(Base):
    __tablename__ = 'users'
    user_id = Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    name = Column(String(100),nullable=False)
    email = Column(String(255),unique=True,nullable=False,index=True)
    password_hash = Column(String(255),nullable=False)
    role = Column(String(10),default='customer')
    created_at = Column(DateTime,default=datetime.utcnow)
    last_login = Column(DateTime,nullable=True)

    orders = relationship('Orders',back_populates='user')



    def __repr__(self):
        return f"<{self.name} has successfully created account {self.created_at}>"
    
    def set_password(self,password):
        self.password_hash = generate_password_hash(password,method="scrypt",salt_length=16)
    def check_password(self,password):
        return check_password_hash(self.password_hash,password) #type: ignore
    
    def to_dict(self):
        ans = {
            'user_id':self.user_id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat() if getattr(self, 'created_at', None) else None,
            'last_login': self.last_login.isoformat() if getattr(self, 'last_login', None) else None
        }
        return ans
        