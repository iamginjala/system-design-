from utils.database import engine,Base
from models import User, Products,OrderItem,Orders,Payments
from utils.logger import get_app_logger

logger = get_app_logger()
def init_database():
    """ create all database tables"""
    Base.metadata.create_all(engine)
    logger.info("Database tables created successfully")

if __name__ == "__main__":
    init_database()
    