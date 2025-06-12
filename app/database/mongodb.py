"""
MongoDB database module
"""

from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import get_settings

# Global database client and connection
db_client: Optional[AsyncIOMotorClient] = None
db: Optional[AsyncIOMotorDatabase] = None


async def connect_to_mongodb() -> None:
    """Connect to MongoDB"""
    global db_client, db
    settings = get_settings()

    # Create MongoDB connection
    db_client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = db_client[settings.MONGODB_DB_NAME]

    # You can add database indexes here
    # Example: await db.collection.create_index([("field", 1)], unique=True)


async def close_mongodb_connection() -> None:
    """Close MongoDB connection"""
    global db_client
    if db_client:
        db_client.close()


def get_database() -> AsyncIOMotorDatabase:
    """Get database connection"""
    return db
