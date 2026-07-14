import os
import json
from neo4j import GraphDatabase, basic_auth
from src.units.parsers import parse_qrel_file
from src.units.myenv import env

# =============================================================================
# Configuration Cell
# =============================================================================
#%%

QUERY_IDS_TO_PROCESS = ['84', '65', '66', '74', '78', '89']
# --- SET THE QUERY ID TO EVALUATE ---
QUERY_ID_TO_EVALUATE = "89" # Corresponds to 'seq2seq'

# --- DATA AND NEO4J CONFIG ---
QUERY_FILE_PATH = "data/Explicit_Semantic_Ranking_Dataset/s2_query.json"
QREL_FILE_PATH = "data/Explicit_Semantic_Ranking_Dataset/s2.qrel"
NEO4J_INDEX_NAME = "entity_text_index"


# =============================================================================
# Initialization Cell
# =============================================================================
#%%
print("--- Initializing Neo4j Connection ---")
try:
    # Initialize the Neo4j driver from environment variables
    driver = GraphDatabase.driver(
        env.get("NEO4J_URI"),
        auth=basic_auth(env.get("NEO4J_USERNAME"), env.get("NEO4J_PASSWORD"))
    )
    driver.verify_connectivity()
    print(f"Neo4j connection verified for URI: {env.get('NEO4J_URI')}")

except Exception as e:
    print(f"An error occurred during Neo4j initialization: {e}")
    exit()

print("-------------------------------------\n")


# =============================================================================
# Load Query and Ground Truth
# =============================================================================
#%%
# --- 1. Load the Query Text ---
print(f"--- Loading Query and Ground Truth for ID: {QUERY_ID_TO_EVALUATE} ---")
query_text = None
try:
    with open(QUERY_FILE_PATH, 'r') as f:
        for line in f:
            data = json.loads(line)
            if data.get('qid') == QUERY_ID_TO_EVALUATE:
                query_text = data.get('query')
                break
except FileNotFoundError:
    print(f"Fatal: Query file not found at {QUERY_FILE_PATH}")
    exit()

if not query_text:
    print(f"Fatal: Query ID '{QUERY_ID_TO_EVALUATE}' not found.")
    exit()

print(f"Evaluating query: '{query_text}'")

# --- 2. Load the Ground Truth (QREL) ---
all_judgments = parse_qrel_file(QREL_FILE_PATH)
if not all_judgments or QUERY_ID_TO_EVALUATE not in all_judgments:
    print(f"Fatal: No relevance judgments found for Query ID {QUERY_ID_TO_EVALUATE}.")
    exit()

# Get the set of relevant doc IDs (score > 0)
relevant_docs = {doc_id for doc_id, score in all_judgments[QUERY_ID_TO_EVALUATE].items() if score > 0}
print(f"Found {len(relevant_docs)} relevant documents in the ground truth.")
print("--------------------------------------------------\n")


# =============================================================================
# Execute Search and Compare
# =============================================================================
#%%
print(f"--- Querying Neo4j using Full-Text Index '{NEO4J_INDEX_NAME}' ---")

# Note: `WHERE node:Document` is not valid Cypher in a WHERE clause.
# The correct way to filter by label is `WHERE 'Document' IN labels(node)`.
q1 = f'''
CALL db.index.fulltext.queryNodes("{NEO4J_INDEX_NAME}", $query_text)
YIELD node, score
WHERE 'Document' IN labels(node) // Correct way to filter by label
RETURN node.doc_id as doc_id
'''

q2 = f'''
CALL db.index.fulltext.queryNodes("{NEO4J_INDEX_NAME}", $query_text)
YIELD node, score
WHERE NOT node:Document
WITH node AS matched_node, score
MATCH (matched_node)-[]-(d:Document)  // Find all Documents linked to matched nodes
WITH d, count(DISTINCT matched_node) AS similarity_score
RETURN d.doc_id as doc_id, similarity_score
ORDER BY similarity_score DESC
'''

q3 = f'''
CALL db.index.fulltext.queryNodes("{NEO4J_INDEX_NAME}", $query_text)
YIELD node, score
WHERE NOT node:Document
WITH node AS matched_node, score
MATCH (matched_node)-[]-(d:Document)  // Find all Documents linked to matched nodes
WITH d, count(DISTINCT matched_node) AS similarity_score
RETURN d.doc_id as doc_id
'''

cypher_query = q3


retrieved_doc_ids = set()
with driver.session() as session:
    result = session.run(cypher_query, query_text=query_text)
    for record in result:
        retrieved_doc_ids.add(record["doc_id"])

print(f"Retrieved {len(retrieved_doc_ids)} documents from Neo4j.")

#%%

# --- 3. Compare and Evaluate ---
print("\n--- Evaluation Results ---")

true_positives = retrieved_doc_ids.intersection(relevant_docs)

# Precision: How many of the retrieved docs were relevant?
precision = len(true_positives) / len(retrieved_doc_ids) if retrieved_doc_ids else 0

# Recall: How many of the relevant docs did we find?
recall = len(true_positives) / len(relevant_docs) if relevant_docs else 0

print(f"  - True Positives (found relevant documents): {len(true_positives)}")
print(f"  - Precision: {precision:.2%}")
print(f"  - Recall:    {recall:.2%}")

print("\n--- Top 5 Retrieved Documents That Are Correct ---")
for doc in list(true_positives)[:5]:
    print(f"  - {doc}")

print("\n--- Evaluation Finished ---")

driver.close()
