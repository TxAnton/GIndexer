import os
import json
from tqdm import tqdm
from langchain_core.documents import Document
from src.units.graph_extractor import GraphExtractor
from src.units.myenv import env
from langchain_neo4j import Neo4jGraph

# =============================================================================
# Configuration Cell
# =============================================================================
#%%
# --- CHOOSE WHICH QUERIES TO PROCESS ---
# Set the list of query file IDs you want to process.
# For example: ['1'] or ['1', '2', '25']
# Leave empty to process all files in the directory.
# QUERY_IDS_TO_PROCESS = ['84', '65', '66', '74', '78', '89']
QUERY_IDS_TO_PROCESS = None

# --- DATA PATHS ---
PER_REQ_DIR = "data/per_req"
S2_DOCS_DIR = "data/s2_docs"

# --- GRAPH SCHEMA ---
# Define the types of nodes and relationships to extract.
ALLOWED_NODES = [
    "ResearchProblem", "Method", "Model", "Dataset", "Framework",
    "Evaluation", "Metric", "Baseline", "Result", "Limitation"
]

# =============================================================================
# Initialization Cell
# =============================================================================
#%%
print("--- Initializing Clients ---")
try:
    # Initialize the graph extractor for turning text into graphs
    extractor = GraphExtractor()

    # Initialize the Neo4j client
    # It will automatically use the NEO4J_URI, NEO4J_USERNAME, and NEO4J_PASSWORD
    # from your .env file, loaded by the myenv unit.
    neo4j_graph = Neo4jGraph()
    print("Neo4j client initialized successfully.")
    print(f"  - URI: {env.get('NEO4J_URI')}")
    print(f"  - User: {env.get('NEO4J_USERNAME')}")

except Exception as e:
    print(f"An error occurred during initialization: {e}")
    print("Please check your .env file and ensure all services are running.")
    exit()

print("--------------------------\n")

# =============================================================================
# Main Processing Cell
# =============================================================================
#%%
# Determine which files to process
if not QUERY_IDS_TO_PROCESS:
    print(f"No specific query IDs provided. Processing all files in {PER_REQ_DIR}...")
    try:
        files_to_process = [os.path.join(PER_REQ_DIR, f) for f in os.listdir(PER_REQ_DIR) if f.endswith('.txt')]
    except FileNotFoundError:
        print(f"Error: Directory not found at {PER_REQ_DIR}")
        files_to_process = []
else:
    files_to_process = [os.path.join(PER_REQ_DIR, f"{qid}.txt") for qid in QUERY_IDS_TO_PROCESS]

print(f"Found {len(files_to_process)} query files to process.")
#%%
graph_documents_list = []
#%%
total_docs = sum(len(open(f, 'r').readlines()) for f in files_to_process if os.path.exists(f))
print(f"Total documents to process across all selected queries: {total_docs}")
#%%
# Process each selected query file
for query_file_path in tqdm(files_to_process, desc="Processing Queries"):
    query_id = os.path.basename(query_file_path).split('.')[0]
    print(f"\n--- Processing Query ID: {query_id} ---")

    try:
        with open(query_file_path, 'r') as f:
            doc_ids = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"  Warning: Query file not found at {query_file_path}. Skipping.")
        continue

    # Loop through each document for the current query
    for doc_id in tqdm(doc_ids, desc=f"Query {query_id} Docs", unit="doc", leave=False):
        doc_json_path = os.path.join(S2_DOCS_DIR, f"{doc_id}.json")

        if not os.path.exists(doc_json_path):
            # print(f"  - Warning: Document file not found for ID {doc_id}. Skipping.") # Too verbose for tqdm
            continue

        # Read the abstract from the document file
        with open(doc_json_path, 'r') as f:
            doc_data = json.load(f)
            abstract = doc_data.get("paperAbstract")

        if not abstract or len(abstract) == 0 or len(abstract[0]) <= 2:
            # print(f"  - Warning: No valid abstract found for document {doc_id}. Skipping.") # Too verbose for tqdm
            continue
        abstract = abstract[0]  # Assuming the abstract is a list and we want the first element
        
        # print(f"  - Processing document {doc_id} with abstract length {len(abstract)} characters.")
        
        fields_metadata = ['paperAbstract', 'numKeyReferences', 'title', 'venue', 'numKeyCitations', 'numCitedBy', 'docno', 'ana']
        doc_metadata = {}
        for field in fields_metadata:
            if field in doc_data:
                if field == 'ana':
                    ana_fields = doc_data[field].keys() if isinstance(doc_data[field], dict) else []
                    for ana_field in ana_fields:
                        if isinstance(doc_data[field][ana_field], dict):
                            doc_metadata[f"ana_{ana_field}"] = list(doc_data[field][ana_field].keys())
                        elif isinstance(doc_data[field][ana_field], list):
                            doc_metadata[f"ana_{ana_field}"] = doc_data[field][ana_field] if doc_data[field] else None

                    doc_metadata[field] = doc_data[field][0] if isinstance(doc_data[field], list) and doc_data[field] else None
                elif isinstance(doc_data[field], list):
                    doc_metadata[field] = doc_data[field][0] if doc_data[field] else None
                else:
                    doc_metadata[field] = doc_data.get(field)
        doc_metadata['doc_id'] = doc_id
        doc_metadata['query_id'] = query_id
        doc_metadata

        # Extract the graph from the abstract
        doc_for_graph = Document(page_content=abstract, metadata=doc_metadata)
        
        try:
            graph_documents = extractor.extract_graph(
                doc_for_graph,
                allowed_nodes=ALLOWED_NODES
            )

            # Ingest the graph into Neo4j, including source metadata
            if graph_documents:
                graph_documents_list.append(graph_documents)
                

        except Exception as e:
            print(f"  - Error processing document {doc_id}: {e}")

#%%
extractor.save_cache()

#%%
print(f"\n--- Finished processing all selected queries. Total graph documents extracted: {len(graph_documents_list)} ---")
print("Ingesting all extracted graph documents into Neo4j...")
for graph_documents in tqdm(graph_documents_list, desc="Ingesting Graphs"):
    neo4j_graph.add_graph_documents(graph_documents, include_source=True)

print("\n--- All selected queries processed successfully! ---")

