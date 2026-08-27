import sys
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable, AuthError
import config

def test_connection():
    uri = config.NEO4J_URI
    user = config.NEO4J_USER
    password = config.NEO4J_PASSWORD

    print(f"Attempting to connect to Neo4j at {uri} as user '{user}'...")

    try:
        # Create a Neo4j driver instance
        driver = GraphDatabase.driver(uri, auth=(user, password))
        
        # Verify the connection
        driver.verify_connectivity()
        print("[SUCCESS] Successfully connected to the Neo4j database!")
        
        # Run a simple query to confirm database operations work
        with driver.session() as session:
            result = session.run("RETURN 'Neo4j connection is fully operational!' AS message")
            for record in result:
                print(f"[SUCCESS] Test query returned: {record['message']}")
                
        driver.close()
    except AuthError as e:
        print(f"[ERROR] Authentication failed: Please check your NEO4J_USER and NEO4J_PASSWORD.\nDetails: {e}")
        sys.exit(1)
    except ServiceUnavailable as e:
        print(f"[ERROR] Service unavailable: Could not connect to {uri}. Check if the database is running and the URI is correct.\nDetails: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Failed to connect to the Neo4j database.\nError: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_connection()
