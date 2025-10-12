from utils.database import engine,Base
from models.order import Orders
from models.product import Products
from models.payment import Payments
from models.order_item import OrderItem
from models.user import User

def init_database():
    """ create all database tables"""
    Base.metadata.create_all(engine)
    print("Database tables created successfully")

if __name__ == "__main__":
    init_database()
    