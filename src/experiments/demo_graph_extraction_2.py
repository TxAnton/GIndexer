
from langchain_core.documents import Document
from src.units.graph_extractor import GraphExtractor
#%%
from tqdm import tqdm
#%%
"""
Example  use of the GraphExtractor unit to extract a graph
from a sample text file.
"""
# 1. Initialize the GraphExtractor
# This handles LLM setup using credentials from the .env file.
try:
    extractor = GraphExtractor()
except ValueError as e:
    print(f"Error initializing extractor: {e}")
    print("Please ensure your .env file is correctly configured.")
    exit(1)
#%%
# 2. Read the sample text content
try:
    with open("/home/a/Documents/asp/artfacts/Ontology-Guided Query Expansion for Biomedical Document Retrieval using Large Language Models.txt", "r") as f:
        sample_text = f.read()
    print("--- Input Text ---")
    print(sample_text)
    print("--------------------")
except FileNotFoundError:
    print("Error: data/sample_text.txt not found.")
    exit(1)
#%%
# 3. Create a Document object for LangChain
doc = Document(page_content=sample_text)

# 4. Define a specific schema for this extraction
allowed_nodes = ["ResearchProblem", "Method", "Model", "Dataset", "Framework", "Evaluation", "TrainingProtocol", "Hardware", "Limitation", "Result", "Metric", "Baseline", "Implementation", "Application", "Finding", "Observation", "Hypothesis"]
allowed_relationships = None
#%%

# 5. Use the extractor to get the graph
# The method encapsulates the transformation logic.
graph_documents = extractor.extract_graph(
    doc,
    allowed_nodes=allowed_nodes,
    # allowed_relationships=allowed_relationships
)

# 6. Print the results using the static method
extractor.print_graphs(graph_documents)
#%%

from langchain_neo4j import Neo4jGraph

graph = Neo4jGraph()

graph.add_graph_documents(graph_documents)


# for graphs in tqdm(graph_documents, desc="Adding graph documents"):
#     graph.add_graph_documents(graphs)


#%%
