# app/api/products/routes.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.config import get_db 
from app.schemas.product import CategoryResponse, ProductCreate, ProductResponse, ProductUpdate, ProductsResponse, SingleProductResponse
from app.api.products.controllers import create_product, delete_product, get_all_categories, get_all_products, get_limited_products, get_product_by_id, get_products_by_category, get_sorted_products, update_product

product = APIRouter()

@product.post("/add/product", response_model=SingleProductResponse)
def add_product(product: ProductCreate, db: Session = Depends(get_db)):
    response = create_product(db, product)
    if response.status == "error":
        raise HTTPException(status_code=400, detail=response.message)
    return response

@product.put("/update/{product_id}", response_model=ProductResponse)
def update_product_route(product_id: int, product_update: ProductUpdate, db: Session = Depends(get_db)):
    response = update_product(db, product_id, product_update)
    if response.status == "error":
        raise HTTPException(status_code=400, detail=response.message)
    return response


@product.delete("/delete/{product_id}", response_model=ProductResponse)
def delete_product_route(product_id: int, db: Session = Depends(get_db)):
    response = delete_product(db, product_id)
    if response.status == "error":
        raise HTTPException(status_code=400, detail=response.message)
    return response


@product.get("/all/products", response_model=ProductsResponse)
def get_all_products_route(db: Session = Depends(get_db)):
    response = get_all_products(db)
    if response.status == "error":
        raise HTTPException(status_code=400, detail=response.message)
    return response


@product.get("/product/{product_id}", response_model=ProductResponse)
def get_product_route(product_id: int, db: Session = Depends(get_db)):
    response = get_product_by_id(db, product_id)
    if response.status == "error":
        raise HTTPException(status_code=404, detail=response.message)
    return response


@product.get("/categories", response_model=CategoryResponse)
def get_all_categories_route(db: Session = Depends(get_db)):
    response = get_all_categories(db)
    if response.status == "error":
        raise HTTPException(status_code=400, detail=response.message)
    return response

@product.get("/category/{category}", response_model=ProductResponse)
def get_products_by_category_route(category: str, db: Session = Depends(get_db)):
    response = get_products_by_category(db, category)
    if response.status == "error":
        raise HTTPException(status_code=400, detail=response.message)
    return response


@product.get("/limited", response_model=ProductResponse)
def get_limited_products_route(limit: int = 10, db: Session = Depends(get_db)):
    response = get_limited_products(db, limit)
    if response.status == "error":
        raise HTTPException(status_code=400, detail=response.message)
    return response


@product.get("/sorted", response_model=ProductResponse)
def get_sorted_products_route(sort_by: str = 'price', order: str = 'asc', db: Session = Depends(get_db)):
    response = get_sorted_products(db, sort_by, order)
    if response.status == "error":
        raise HTTPException(status_code=400, detail=response.message)
    return response


