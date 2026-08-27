"""
database.py
-----------
Neo4j connection manager for the FastAPI backend.
Single driver instance shared across all requests (connection pooling).
"""

import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

_driver = None


def get_driver():
    global _driver
    if _driver is None:
        uri      = os.getenv("NEO4J_URI")
        user     = os.getenv("NEO4J_USER") or os.getenv("NEO4J_USERNAME") or "neo4j"
        password = os.getenv("NEO4J_PASSWORD")

        if not uri or not password:
            raise RuntimeError(
                "NEO4J_URI and NEO4J_PASSWORD must be set in .env file"
            )

        driver = GraphDatabase.driver(uri, auth=(user, password))
        driver.verify_connectivity()
        _driver = driver

    return _driver


def close_driver():
    global _driver
    if _driver:
        _driver.close()
        _driver = None
