

import pandas as pd
from tqdm import tqdm

from langchain_core.documents import Document
from src.units.graph_extractor import GraphExtractor

#%%
extractor = GraphExtractor()
#%%

data = pd.read_csv('data/merged_snippet.csv')
len(data)

#%%


#%%

# Process abstracts and extract graphs
allowed_nodes = ["ResearchProblem", "Method", "Model", "Dataset", "Framework", "Evaluation", "TrainingProtocol", "Hardware"]
allowed_relationships = None
#%%
graph_documents_list = []
#%%
for index, row in tqdm(data.iterrows(), total=len(data), desc="Processing abstracts"):
    doc = Document(page_content=row['abstract'])
    graph_documents = extractor.extract_graph(
        doc,
        allowed_nodes=allowed_nodes,
        allowed_relationships=allowed_relationships
    )
    graph_documents_list.append(graph_documents)
#%%
# Optional: print extracted graphs
for graphs in graph_documents_list:
    extractor.print_graphs(graphs)

#%%

from langchain_neo4j import Neo4jGraph

graph = Neo4jGraph()
#%%
for graphs in tqdm(graph_documents_list, desc="Adding graph documents"):
    graph.add_graph_documents(graphs)

