import os
import json
import numpy as np
from tqdm import tqdm
from neo4j import GraphDatabase, basic_auth
from src.units.parsers import parse_qrel_file
from src.units.myenv import env

# =============================================================================
# Configuration Cell
# =============================================================================
#%%
# --- SET THE QUERY IDs TO EVALUATE ---
# An empty list will process all available queries in the QREL file.
QUERY_IDS_TO_EVALUATE = ['84', '65', '66', '74', '78', '89']

# --- DATA AND NEO4J CONFIG ---
QUERY_FILE_PATH = "data/Explicit_Semantic_Ranking_Dataset/s2_query.json"
QREL_FILE_PATH = "data/Explicit_Semantic_Ranking_Dataset/s2.qrel"
NEO4J_INDEX_NAME = "entity_text_index"

# --- CHOOSE THE CYPHER QUERY TO RUN ---
# q1: Direct document search.
# q3: Find linked documents via non-document nodes.
CYPHER_QUERY_CHOICE = 'q3'

# =============================================================================
# Initialization Cell
# =============================================================================
#%%
print("--- Initializing Neo4j Connection ---")
try:
    driver = GraphDatabase.driver(
        env.get("NEO4J_URI"),
        auth=basic_auth(env.get("NEO4J_USERNAME"), env.get("NEO4J_PASSWORD"))
    )
    driver.verify_connectivity()
    print(f"Neo4j connection verified.")
except Exception as e:
    print(f"An error occurred during Neo4j initialization: {e}")
    exit()
print("-------------------------------------\n")

# =============================================================================
# Load All Data
# =============================================================================
#%%
# --- 1. Load All Queries into a Dictionary ---
print(f"--- Loading all data ---")
all_queries = {}
try:
    with open(QUERY_FILE_PATH, 'r') as f:
        for line in f:
            data = json.loads(line)
            all_queries[data['qid']] = data['query']
    print(f"Loaded {len(all_queries)} queries from {QUERY_FILE_PATH}")
except FileNotFoundError:
    print(f"Fatal: Query file not found at {QUERY_FILE_PATH}")
    driver.close()
    exit()

# --- 2. Load All Ground Truth Judgments ---
all_judgments = parse_qrel_file(QREL_FILE_PATH)
if not all_judgments:
    print(f"Fatal: Could not parse QREL file at {QREL_FILE_PATH}")
    driver.close()
    exit()
print("------------------------\n")

# =============================================================================
# Batch Evaluation Loop
# =============================================================================
#%%
evaluation_results = []

# If QUERY_IDS_TO_EVALUATE is empty, use all queries that have judgments
queries_to_process = QUERY_IDS_TO_EVALUATE or all_judgments.keys()

for query_id in tqdm(queries_to_process, desc="Evaluating Queries"):

    # --- Get Query and Relevant Docs ---
    query_text = all_queries.get(query_id)
    if not query_text:
        # tqdm.write(f"Warning: Query ID {query_id} not found in query file. Skipping.")
        continue

    judgments_for_query = all_judgments.get(query_id, {})
    relevant_docs = {doc_id for doc_id, score in judgments_for_query.items() if score > 0}

    if not relevant_docs:
        # tqdm.write(f"Warning: No relevant documents found for Query ID {query_id}. Skipping evaluation for this query.")
        continue

    # --- Execute Search ---
    cypher_queries = {
        'q1': f'''
            CALL db.index.fulltext.queryNodes("{NEO4J_INDEX_NAME}", $query_text)
            YIELD node, score WHERE 'Document' IN labels(node)
            RETURN node.doc_id as doc_id
        ''',
        'q3': f'''
            CALL db.index.fulltext.queryNodes("{NEO4J_INDEX_NAME}", $query_text)
            YIELD node, score WHERE NOT 'Document' IN labels(node)
            WITH node AS matched_node
            MATCH (matched_node)-[]-(d:Document)
            RETURN DISTINCT d.doc_id as doc_id
        '''
    }
    cypher_query = cypher_queries[CYPHER_QUERY_CHOICE]

    with driver.session() as session:
        result = session.run(cypher_query, query_text=query_text)
        retrieved_doc_ids = {record["doc_id"] for record in result}

    # --- Calculate Metrics ---
    true_positives = retrieved_doc_ids.intersection(relevant_docs)
    precision = len(true_positives) / len(retrieved_doc_ids) if retrieved_doc_ids else 0
    recall = len(true_positives) / len(relevant_docs)

    evaluation_results.append({
        "query_id": query_id,
        "true_positives": len(true_positives),
        "precision": precision,
        "recall": recall
    })

print("\n--- Batch Evaluation Complete ---")

# =============================================================================
# Aggregate and Display Results
# =============================================================================
#%%
if evaluation_results:
    avg_precision = np.mean([res["precision"] for res in evaluation_results])
    avg_recall = np.mean([res["recall"] for res in evaluation_results])

    print("\n--- AGGREGATE RESULTS ---")
    print(f"  Queries Evaluated: {len(evaluation_results)}")
    print(f"  Mean Precision:    {avg_precision:.2%}")
    print(f"  Mean Recall:       {avg_recall:.2%}")
    print("-------------------------")

    # Write per-query results and aggregate means to CSV
    try:
        import csv
        out_path = "data/res/batch_evaluation_results.csv"
        with open(out_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerow(["query_id", "true_positives", "precision", "recall"])
            for res in evaluation_results:
                writer.writerow([res["query_id"], res["true_positives"], f"{res["precision"]:.6f}", f"{res["recall"]:.6f}"])
            # write mean row
            writer.writerow(["MEAN", "", f"{avg_precision:.6f}", f"{avg_recall:.6f}"])
        print(f"Wrote detailed results to {out_path}")
    except Exception as e:
        print(f"Warning: Failed to write CSV results: {e}")

    # print("\n--- Individual Query Results ---")
    # for res in evaluation_results:
    #     print(f"  ID {res['query_id']:<5} | Precision: {res['precision']:>7.2%}, Recall: {res['recall']:>7.2%}")

driver.close()

#%%

# write query_id	true_positives	precision	recall to a scv file for each query and also mean
