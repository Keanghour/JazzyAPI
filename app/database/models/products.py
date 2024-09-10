from sqlalchemy import Column, Float, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database.config import Base  # Import Base from your database setup

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    price = Column(Float)
    description = Column(Text)
    brand = Column(String, nullable=True)
    model = Column(String, nullable=True)
    color = Column(String, nullable=True)
    category = Column(String)
    image = Column(String, nullable=True)  # Base64 encoded image
    discountPercentage = Column(Float, nullable=True)
    stockQuantity = Column(Integer, nullable=True)
    rating_rate = Column(Float, nullable=True)
    rating_count = Column(Integer, nullable=True)
    availabilityStatus = Column(String, nullable=True)
    
    # If you have relationships, define them here (e.g., with Category)

