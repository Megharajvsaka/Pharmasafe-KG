"""
neo4j.py
--------
Neo4j Graph Database driver singleton with automatic reconnection handling.
"""

from typing import Optional
from neo4j import GraphDatabase, Driver
from backend.app.core.config import settings

_driver_instance: Optional[Driver] = None


def get_driver() -> Driver:
    """Returns the shared Neo4j driver instance with connection pooling."""
    global _driver_instance
    if _driver_instance is None or getattr(_driver_instance, "_closed", False):
        _driver_instance = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD),
            max_connection_lifetime=3600,
            max_connection_pool_size=50,
            connection_acquisition_timeout=30.0,
        )
    return _driver_instance


def close_driver():
    """Cleanly close Neo4j connection pool."""
    global _driver_instance
    if _driver_instance is not None:
        try:
            _driver_instance.close()
        except Exception:
            pass
        _driver_instance = None
