from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from app.routes import invoice_routes, expense_routes, test_routes
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database initialization
@app.on_event("startup")
async def startup_db_client():
    app.mongodb_client = AsyncIOMotorClient(os.getenv("MONGODB_URL"))
    app.database = app.mongodb_client.solopreneur_db

@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongodb_client.close()

# Include routers
app.include_router(test_routes.router, prefix="/api/test", tags=["test"])
app.include_router(invoice_routes.router, prefix="/api/invoices", tags=["invoices"])
app.include_router(expense_routes.router, prefix="/api/expenses", tags=["expenses"])
app.include_router(test_routes.router, prefix="/api/test", tags=["test"])

@app.get("/")
async def root():
    return {"message": "Welcome to Solopreneur Financial Tool API"}