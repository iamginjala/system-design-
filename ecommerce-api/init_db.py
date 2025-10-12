from utils.database import engine,Base
from models import User, Products,OrderItem,Orders,Payments

def init_database():
    """ create all database tables"""
    Base.metadata.create_all(engine)
    print("Database tables created successfully")

if __name__ == "__main__":
    init_database()
    