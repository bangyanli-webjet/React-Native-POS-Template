from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime
from bson import ObjectId

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Custom ObjectId field for Pydantic
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

# Product Models
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = ""
    price: float = Field(..., gt=0)
    stock: int = Field(..., ge=0)
    category: str = "General"
    image: Optional[str] = None  # base64 string
    is_active: bool = True

class Product(ProductBase):
    id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    category: Optional[str] = None
    image: Optional[str] = None
    is_active: Optional[bool] = None

# Transaction Models
class TransactionItem(BaseModel):
    product_id: str
    product_name: str
    price: float
    quantity: int
    total: float

class TransactionBase(BaseModel):
    items: List[TransactionItem]
    subtotal: float
    tax: float = 0.0
    discount: float = 0.0
    total: float
    payment_method: str = "cash"  # cash, card, digital
    customer_name: Optional[str] = None
    notes: Optional[str] = None

class Transaction(TransactionBase):
    id: Optional[str] = None
    transaction_number: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "completed"

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class TransactionCreate(TransactionBase):
    pass

# Utility functions
def format_doc(doc):
    """Convert MongoDB document to JSON serializable format"""
    if doc and "_id" in doc:
        doc["id"] = str(doc["_id"])
        del doc["_id"]
    return doc

# Product endpoints
@api_router.get("/products", response_model=List[Product])
async def get_products(
    category: Optional[str] = None,
    active_only: bool = True,
    limit: int = 100
):
    """Get all products with optional filtering"""
    filter_query = {}
    if category:
        filter_query["category"] = category
    if active_only:
        filter_query["is_active"] = True
    
    cursor = db.products.find(filter_query).limit(limit)
    products = await cursor.to_list(length=limit)
    return [format_doc(product) for product in products]

@api_router.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: str):
    """Get a specific product by ID"""
    if not ObjectId.is_valid(product_id):
        raise HTTPException(status_code=400, detail="Invalid product ID")
    
    product = await db.products.find_one({"_id": ObjectId(product_id)})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return format_doc(product)

@api_router.post("/products", response_model=Product)
async def create_product(product: ProductCreate):
    """Create a new product"""
    product_dict = product.dict()
    product_dict["created_at"] = datetime.utcnow()
    product_dict["updated_at"] = datetime.utcnow()
    
    result = await db.products.insert_one(product_dict)
    created_product = await db.products.find_one({"_id": result.inserted_id})
    
    return format_doc(created_product)

@api_router.put("/products/{product_id}", response_model=Product)
async def update_product(product_id: str, product_update: ProductUpdate):
    """Update an existing product"""
    if not ObjectId.is_valid(product_id):
        raise HTTPException(status_code=400, detail="Invalid product ID")
    
    update_dict = {k: v for k, v in product_update.dict().items() if v is not None}
    if not update_dict:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    update_dict["updated_at"] = datetime.utcnow()
    
    result = await db.products.update_one(
        {"_id": ObjectId(product_id)},
        {"$set": update_dict}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    
    updated_product = await db.products.find_one({"_id": ObjectId(product_id)})
    return format_doc(updated_product)

@api_router.delete("/products/{product_id}")
async def delete_product(product_id: str):
    """Delete a product (soft delete by setting is_active to False)"""
    if not ObjectId.is_valid(product_id):
        raise HTTPException(status_code=400, detail="Invalid product ID")
    
    result = await db.products.update_one(
        {"_id": ObjectId(product_id)},
        {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return {"message": "Product deleted successfully"}

# Transaction endpoints
@api_router.get("/transactions", response_model=List[Transaction])
async def get_transactions(limit: int = 50, skip: int = 0):
    """Get all transactions with pagination"""
    cursor = db.transactions.find().sort("created_at", -1).skip(skip).limit(limit)
    transactions = await cursor.to_list(length=limit)
    return [format_doc(transaction) for transaction in transactions]

@api_router.get("/transactions/{transaction_id}", response_model=Transaction)
async def get_transaction(transaction_id: str):
    """Get a specific transaction by ID"""
    if not ObjectId.is_valid(transaction_id):
        raise HTTPException(status_code=400, detail="Invalid transaction ID")
    
    transaction = await db.transactions.find_one({"_id": ObjectId(transaction_id)})
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    return format_doc(transaction)

@api_router.post("/transactions", response_model=Transaction)
async def create_transaction(transaction: TransactionCreate):
    """Create a new transaction and update product stock"""
    transaction_dict = transaction.dict()
    
    # Generate transaction number
    count = await db.transactions.count_documents({})
    transaction_dict["transaction_number"] = f"TXN-{count + 1:06d}"
    transaction_dict["created_at"] = datetime.utcnow()
    transaction_dict["status"] = "completed"
    
    # Update product stock for each item
    for item in transaction.items:
        if ObjectId.is_valid(item.product_id):
            await db.products.update_one(
                {"_id": ObjectId(item.product_id)},
                {"$inc": {"stock": -item.quantity}, "$set": {"updated_at": datetime.utcnow()}}
            )
    
    result = await db.transactions.insert_one(transaction_dict)
    created_transaction = await db.transactions.find_one({"_id": result.inserted_id})
    
    return format_doc(created_transaction)

# Category endpoints
@api_router.get("/categories")
async def get_categories():
    """Get all unique product categories"""
    categories = await db.products.distinct("category", {"is_active": True})
    return {"categories": categories}

# Dashboard/Analytics endpoints
@api_router.get("/dashboard/stats")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    total_products = await db.products.count_documents({"is_active": True})
    total_transactions = await db.transactions.count_documents({})
    
    # Get today's sales
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_sales = await db.transactions.aggregate([
        {"$match": {"created_at": {"$gte": today_start}}},
        {"$group": {"_id": None, "total": {"$sum": "$total"}, "count": {"$sum": 1}}}
    ]).to_list(1)
    
    today_revenue = today_sales[0]["total"] if today_sales else 0
    today_transactions = today_sales[0]["count"] if today_sales else 0
    
    # Low stock products (stock < 10)
    low_stock_count = await db.products.count_documents({"stock": {"$lt": 10}, "is_active": True})
    
    return {
        "total_products": total_products,
        "total_transactions": total_transactions,
        "today_revenue": today_revenue,
        "today_transactions": today_transactions,
        "low_stock_count": low_stock_count
    }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()