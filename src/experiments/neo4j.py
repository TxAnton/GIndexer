
import os
import sys
from neo4j import GraphDatabase, basic_auth
from src.units.myenv import env as myenv
#%%

uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
user = os.environ.get("NEO4J_USERNAME", "neo4j")
password = os.environ.get("NEO4J_PASSWORD")
limit = int(os.environ.get("NODES_LIMIT", "25"))


#%%
driver = GraphDatabase.driver(uri, auth=basic_auth(user, password))

query = "MATCH (n) RETURN n LIMIT $limit"

with driver.session() as session:
    result = session.run(query, limit=limit)
    count = 0
    for record in result:
        node = record.get("n")
        # node: neo4j.graph.Node
        props = dict(node)
        print(f"id={node.id} labels={list(node.labels)} properties={props}")
        count += 1

print(f"Listed {count} nodes")
#%%

# create a new database for the experiment
driver = GraphDatabase.driver(uri, auth=basic_auth(user, password))
with driver.session() as session:
    # Create a new database named "exp"
    session.run("CREATE DATABASE exp")
    print("Created new database 'exp'")
    

#%%

from langchain_neo4j import Neo4jGraph

graph = Neo4jGraph()
#%%
graph.add_graph_documents
#%%
!pip install langchain_neo4j

#%%
!pip install neo4j 