import os
import json
from tqdm import tqdm
from langchain_openai import ChatOpenAI
from langchain_neo4j import Neo4jGraph, GraphCypherQAChain
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)

# This import loads the .env file into the environment
from src.units.myenv import env

# =============================================================================
# Configuration Cell
# =============================================================================
#%%
QUERY_IDS_TO_PROCESS = ['84', '65', '66', '74', '78', '89']
# --- SET THE QUERY ID YOU WANT TO RUN ---
QUERY_ID_TO_RUN = "84" 

# --- DATA AND API CONFIG ---
QUERY_FILE_PATH = "data/Explicit_Semantic_Ranking_Dataset/s2_query.json"

# =============================================================================
# Prompt Engineering
# =============================================================================
CUSTOM_CYPHER_PROMPT = ChatPromptTemplate.from_messages(
    [
        SystemMessagePromptTemplate.from_template(
            "You are a Neo4j query generator. Translate the natural language question into a Cypher query."
        ),
        HumanMessagePromptTemplate.from_template(
            "Given the graph schema and a question, first identify all entities "
            "whose labels or properties are similar to the query text. Use following cypher query to find the entities: "
            "CALL db.index.fulltext.queryNodes(\"entity_text_index\", \"john\") YIELD node, score RETURN node.id, node.text, score ;"
            "Then return "
            "all documents connected to those entities. Use only Cypher and do not "
            "include any explanation.\n\n"
            "Schema:\n{schema}\n\nQuestion:\n{question}"
        ),
    ]
)

# =============================================================================
# Initialization Cell
# =============================================================================
#%%
print("--- Initializing Clients and QA Chain ---")
try:
    # Initialize the LLM from environment variables
    llm = ChatOpenAI(
        model=env.get("OPENAI_MODEL"),
        api_key=env.get("OPENAI_API_KEY"),
        base_url=env.get("OPENAI_API_BASE"),
        temperature=0
    )
    print("LLM initialized successfully.")

    # Initialize the Neo4j Graph connection
    graph = Neo4jGraph()
    print(f"Neo4jGraph connected to URI: {env.get('NEO4J_URI')}")

    # Create the Graph Cypher QA Chain
    chain = GraphCypherQAChain.from_llm(
        graph=graph,
        llm=llm,
        cypher_prompt=CUSTOM_CYPHER_PROMPT,
        verbose=True,
        validate_cypher=True, # Helps prevent syntax errors in generated Cypher
        return_intermediate_steps=True, # Crucial for seeing the generated query,
        allow_dangerous_requests=True 
    )
    print("GraphCypherQAChain created and ready.")

except Exception as e:
    print(f"An error occurred during initialization: {e}")
    print("Please check your .env file and ensure all services are running.")
    exit()

print("---------------------------------------\n")

# =============================================================================
# Load Query Text Cell
# =============================================================================
#%%
print(f"--- Searching for Query ID: {QUERY_ID_TO_RUN} in {QUERY_FILE_PATH} ---")
query_text = None
try:
    with open(QUERY_FILE_PATH, 'r') as f:
        for line in f:
            data = json.loads(line)
            if data.get('qid') == QUERY_ID_TO_RUN:
                query_text = data.get('query')
                print(f"Found query: '{query_text}'")
                break
except FileNotFoundError:
    print(f"Error: Query file not found at {QUERY_FILE_PATH}")
    exit()

if not query_text:
    print(f"Error: Query ID '{QUERY_ID_TO_RUN}' not found in the file.")
    exit()

print("--------------------------------------------------\n")

# =============================================================================
# Execute Query Cell
# =============================================================================
#%%
query = query_text

#%%

print(f"--- Executing query against the graph ---")
response = chain.invoke({"query": query})

print("\n--- Query Execution Complete ---")

# Print the results in a structured way
print("\n================ [ FINAL ANSWER ] ================")
print(response.get('result'))
print("==================================================\n")

if response.get('intermediate_steps'):
    print("========== [ INTERMEDIATE STEPS ] ===========")
    for i, step in enumerate(response['intermediate_steps'], 1):
        print(f"--- Step {i}: Generated Cypher ---")
        print(step.get("query"))
        print(f"\n--- Step {i}: Cypher Result (Context) ---")
        print(step.get("context"))
        print("-------------------------------------")
    print("============================================\n")
