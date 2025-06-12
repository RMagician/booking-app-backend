"""
Package init for database module
"""

from app.database.mongodb import (
    connect_to_mongodb,
    close_mongodb_connection,
    get_database,
)

__all__ = ["connect_to_mongodb", "close_mongodb_connection", "get_database"]
