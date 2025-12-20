# Model represents table and model instances are rows in the table

from sqlalchemy import Column, Integer, String, Float
from database import Base

class Employee(Base):
    __tablename__ = 'employees'
    
    id = Column(Integer, primary_key = True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    age = Column(Integer)
    department = Column(String)
    salary = Column(Float)