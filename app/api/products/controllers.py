# app/api/products/controllers.py

from sqlalchemy import distinct
from sqlalchemy.orm import Session
from app.schemas.product import CategoryResponse, ProductCreate, ProductResponse, ProductUpdate, ProductBase, ProductsResponse, SingleProductResponse
from app.database.models.products import Product
from sqlalchemy.exc import NoResultFound

def create_product(db: Session, product: ProductCreate) -> ProductResponse:
    try:
        db_product = Product(
            title=product.title,
            price=product.price,
            description=product.description,
            brand=product.brand,
            model=product.model,
            color=product.color,
            category=product.category,
            image=product.image,
            discountPercentage=product.discountPercentage,
            stockQuantity=product.stockQuantity,
            rating_rate=product.rating.rate if product.rating else None,
            rating_count=product.rating.count if product.rating else None,
            availabilityStatus=product.availabilityStatus
        )
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        # Debug print
        print(f"Created Product: {db_product}")

        return SingleProductResponse(
            status="success",
            message="Product created successfully",
            data=ProductBase.from_orm(db_product)
        )
    except Exception as e:
        return SingleProductResponse(
            status="error",
            message=str(e),
            data=None
        )


def update_product(db: Session, product_id: int, product_update: ProductUpdate) -> ProductResponse:
    try:
        db_product = db.query(Product).filter(Product.id == product_id).first()
        if db_product is None:
            return ProductResponse(
                status="error",
                message="Product not found",
                data=None
            )
        
        for attr, value in vars(product_update).items():
            if value is not None:
                setattr(db_product, attr, value)
        
        db.commit()
        db.refresh(db_product)
        
        return ProductResponse(
            status="success",
            message="Product updated successfully",
            data=ProductBase.from_orm(db_product)
        )
    except NoResultFound:
        return ProductResponse(
            status="error",
            message="Product not found",
            data=None
        )
    except Exception as e:
        return ProductResponse(
            status="error",
            message=str(e),
            data=None
        )


def delete_product(db: Session, product_id: int) -> ProductResponse:
    try:
        db_product = db.query(Product).filter(Product.id == product_id).first()
        if db_product is None:
            return ProductResponse(
                status="error",
                message="Product not found",
                data=None
            )
        
        db.delete(db_product)
        db.commit()
        
        return ProductResponse(
            status="success",
            message="Product deleted successfully",
            data=None
        )
    except NoResultFound:
        return ProductResponse(
            status="error",
            message="Product not found",
            data=None
        )
    except Exception as e:
        return ProductResponse(
            status="error",
            message=str(e),
            data=None
        )
    

def get_all_products(db: Session) -> ProductsResponse:
    try:
        products = db.query(Product).all()
        product_list = [ProductBase.from_orm(product) for product in products]
        
        return ProductsResponse(
            status="success",
            message="Products retrieved successfully",
            data=product_list
        )
    except Exception as e:
        return ProductsResponse(
            status="error",
            message=str(e),
            data=[]
        )
    

def get_product_by_id(db: Session, product_id: int) -> ProductResponse:
    try:
        db_product = db.query(Product).filter(Product.id == product_id).first()
        if db_product is None:
            return ProductResponse(
                status="error",
                message="Product not found",
                data=None
            )
        product_data = ProductBase.from_orm(db_product)
        return ProductResponse(
            status="success",
            message="Product retrieved successfully",
            data=product_data
        )
    except Exception as e:
        return ProductResponse(
            status="error",
            message=str(e),
            data=None
        )
    

def get_all_categories(db: Session) -> CategoryResponse:
    try:
        categories = db.query(distinct(Product.category)).all()
        category_list = [category[0] for category in categories]
        
        return CategoryResponse(
            status="success",
            message="Categories retrieved successfully",
            data=category_list
        )
    except Exception as e:
        return CategoryResponse(
            status="error",
            message=str(e),
            data=None
        )

def get_products_by_category(db: Session, category: str) -> ProductResponse:
    try:
        products = db.query(Product).filter(Product.category == category).all()
        product_list = [ProductBase.from_orm(product) for product in products]
        
        return ProductResponse(
            status="success",
            message="Products retrieved successfully",
            data=product_list
        )
    except Exception as e:
        return ProductResponse(
            status="error",
            message=str(e),
            data=None
        )
    


def get_limited_products(db: Session, limit: int) -> ProductResponse:
    try:
        products = db.query(Product).limit(limit).all()
        product_list = [ProductBase.from_orm(product) for product in products]
        
        return ProductResponse(
            status="success",
            message="Limited products retrieved successfully",
            data=product_list
        )
    except Exception as e:
        return ProductResponse(
            status="error",
            message=str(e),
            data=None
        )
    

def get_sorted_products(db: Session, sort_by: str, order: str) -> ProductResponse:
    try:
        if order == 'asc':
            products = db.query(Product).order_by(getattr(Product, sort_by).asc()).all()
        elif order == 'desc':
            products = db.query(Product).order_by(getattr(Product, sort_by).desc()).all()
        else:
            return ProductResponse(
                status="error",
                message="Invalid order parameter. Use 'asc' or 'desc'.",
                data=None
            )
        
        product_list = [ProductBase.from_orm(product) for product in products]
        
        return ProductResponse(
            status="success",
            message="Sorted products retrieved successfully",
            data=product_list
        )
    except Exception as e:
        return ProductResponse(
            status="error",
            message=str(e),
            data=None
        )
    


    