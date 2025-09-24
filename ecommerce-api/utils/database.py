import os
import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base

# DATABSE DETAILS

DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')

## DATABASE URL

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
Base = declarative_base()


try:
    conn = psycopg2.connect(host = DB_HOST,database = DB_NAME
                            ,user=DB_USER,password = DB_PASSWORD
                            ,port = DB_PORT)
    print("Successfully connected to PostgreSQL!")
    conn.close()
except psycopg2.Error as e:
    print(f"Error connecting to PostgreSQL: {e}")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, 
  bind=engine)