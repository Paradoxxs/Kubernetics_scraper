import sqlite3
from neo4j import GraphDatabase

# SQLite connection
sqlite_conn = sqlite3.connect('shellsec.pw/shellsec.db')
sqlite_cursor = sqlite_conn.cursor()

# Neo4j connection
neo4j_driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
neo4j_session = neo4j_driver.session()

# Retrieve data from SQLite
sqlite_cursor.execute("SELECT author, thread_name FROM posts")
rows = sqlite_cursor.fetchall()

# Import data into Neo4j
for row in rows:
    author, thread_name = row
    query = """
    MERGE (a:Author {name: $author})
    MERGE (t:Thread {name: $thread_name})
    MERGE (a)-[:AUTHOR_OF]->(t)
    """
    neo4j_session.run(query, author=author, thread_name=thread_name)

# Close connections
sqlite_cursor.close()
sqlite_conn.close()
neo4j_session.close()
neo4j_driver.close()
