from pydantic import BaseModel
from typing import Optional, List

class Rating(BaseModel):
    rate: Optional[float] = None
    count: Optional[int] = None

class ProductBase(BaseModel):
    title: str
    price: float
    description: str
    brand: Optional[str] = None
    model: Optional[str] = None
    color: Optional[str] = None
    category: str
    image: Optional[str] = None
    discountPercentage: Optional[float] = None
    stockQuantity: Optional[int] = None
    rating: Optional[Rating] = None
    availabilityStatus: Optional[str] = None

    class Config:
        from_attributes = True

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    title: Optional[str] = None
    price: Optional[float] = None
    description: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    color: Optional[str] = None
    category: Optional[str] = None
    image: Optional[str] = None
    discountPercentage: Optional[float] = None
    stockQuantity: Optional[int] = None
    rating: Optional[Rating] = None
    availabilityStatus: Optional[str] = None

class ProductResponse(BaseModel):
    status: str
    message: str
    data: Optional[List[ProductBase]] = None 

class SingleProductResponse(BaseModel):
    status: str
    message: str
    data: Optional[ProductBase] = None  # Single product details

    class Config:
        from_attributes = True

class ProductsResponse(BaseModel):
    status: str
    message: str
    data: List[ProductBase]

class CategoryResponse(BaseModel):
    status: str
    message: str
    data: Optional[List[str]] = None  # List of category names