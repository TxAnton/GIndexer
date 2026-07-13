from langchain_openai import ChatOpenAI
from neo4j import GraphDatabase
from neo4j_graphrag.retrievers import VectorRetriever
from neo4j_graphrag.llm import OpenAILLM
from neo4j_graphrag.generation import GraphRAG
from neo4j_graphrag.embeddings import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
# from langchain_classic.chains import GraphCypherQAChain
from langchain_neo4j import Neo4jGraph, GraphCypherQAChain
#%%
# ModuleNotFoundError: No module named 'langchain.chains'
!pip install langchain[all]
#%%
from src.units.myenv import env as myenv
import os
#%%

# 1. Neo4j driver

INDEX_NAME = "index-name"

# Connect to Neo4j database
#%%
uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
user = os.environ.get("NEO4J_USERNAME", "neo4j")
password = os.environ.get("NEO4J_PASSWORD")
limit = int(os.environ.get("NODES_LIMIT", "25"))

#%%
api_key = os.getenv("OPENAI_API_KEY")
api_base = os.getenv("OPENAI_API_BASE")
model = os.getenv("OPENAI_MODEL")

#%%
driver = GraphDatabase.driver(uri, auth=(user, password))
#%%
# 2. Retriever
# Create Embedder object, needed to convert the user question (text) to a vector
embedder = OpenAIEmbeddings(model="openai/text-embedding-3-large", api_key=api_key, base_url=api_base)

#%%
# # create index if it doesn't exist
# with driver.session() as session:
#     session.run(f"CREATE FULLTEXT INDEX {INDEX_NAME} IF NOT EXISTS FOR (n) ON EACH [n.title, n.content]")
#     print(f"Fulltext index '{INDEX_NAME}' created or already exists.")

#%%
# Initialize the retriever
# retriever = VectorRetriever(driver, INDEX_NAME, embedder)
# #%%
llm = ChatOpenAI(
        model=model,
        api_key=api_key,
        base_url=api_base,
        temperature=0
    )
#%%
# 3. LLM
# Note: the OPENAI_API_KEY must be in the env vars
# llm = OpenAILLM(model_name=model, model_params={"temperature": 0}, api_key=api_key, base_url=api_base)

#%%

from langchain_neo4j import Neo4jGraph

graph = Neo4jGraph()



#%%


chain = GraphCypherQAChain.from_llm(
            graph=graph,
            llm=llm,
            verbose=True,
            validate_cypher=True,
            allow_dangerous_requests=True,
            return_intermediate_steps=True
        )

#%%

response = chain.invoke({"query": "Can you summarise the document?"})
#%%
response = chain.invoke({"query": "How do I do similarity search in Neo4j?"})
#%%
# response = chain.invoke({"query": "What can you tell about id: Audio Source Separation Research Problem?"})
# response = chain.invoke({"query": "What does End-To-End Source Separation method uses?"})
response = chain.invoke({"query": "What document mentions End-To-End Source Separation method?"})
response
#%%
# Initialize the RAG pipeline
rag = GraphRAG(retriever=retriever, llm=llm)
#%%
# Query the graph
query_text = "How do I do similarity search in Neo4j?"
response = rag.search(query_text=query_text, retriever_config={"top_k": 5})
print(response.answer)