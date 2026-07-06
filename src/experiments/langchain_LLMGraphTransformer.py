
import os
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document
from langchain_experimental.graph_transformers import LLMGraphTransformer

from src.units.myenv import env

#%%


"""
This script demonstrates how to use the LLMGraphTransformer to convert
unstructured text into a graph structure (nodes and relationships).
"""
#%%
# 1. Read the example text file from the 'data' directory
try:
    with open("data/sample_text.txt", "r") as f:
        sample_text = f.read()
    print("--- Input Text ---")
    print(sample_text)
    print("\n" + "="*20 + "\n")
except FileNotFoundError:
    print("Error: data/sample_text.txt not found.")
    print("Please make sure the file exists and contains some text.")

#%%

# 2. Define the graph schema: allowed node and relationship types
# This provides a structure for the language model to follow,
# improving consistency and quality of the output graph.
allowed_nodes = ["Person", "Organization", "Location"]
allowed_relationships = ["WORKS_AT", "IS_A", "LOCATED_IN", "WORKS_WITH"]
#%%
# 3. Instantiate the language model and the graph transformer
# Using a specific model and setting temperature to 0 for deterministic output.

# Use env.OPENAI_API_KEY, env.OPENAI_API_BASE, and env.OPENAI_MODEL to initialize the ChatOpenAI instance.

llm = ChatOpenAI(
    model=env.OPENAI_MODEL,
    temperature=0,
    max_retries=3,
    max_tokens=None,
    timeout=None,
    api_key=env.OPENAI_API_KEY,
    base_url=env.OPENAI_API_BASE
)

#%%

#%%
# process doc to graph. No limit on allowed nodes and relationships
def extract_graph(llm, doc, allowed_nodes = None, allowed_relationships = None):

    llm_transformer_unrestricted = LLMGraphTransformer(
    llm=llm,
    allowed_nodes=None,
    allowed_relationships=None,
)

    graph_docs_full = llm_transformer_unrestricted.convert_to_graph_documents([doc])
    return graph_docs_full



#%%
# 4. Process the text into a graph
# The raw text is wrapped in a LangChain Document object.
doc = Document(page_content=sample_text)

graph_documents = extract_graph(llm, doc, allowed_nodes=allowed_nodes, allowed_relationships=allowed_relationships)

#%%

# 5. Print the resulting graph structure
# The result is a list of GraphDocument objects.
def print_graphs(graph_documents):
    if graph_documents:
        graph = graph_documents[0]
        print("--- Output Graph ---")
        print("Nodes:")
        for node in graph.nodes:
            print(f"  - {node}")

        print("\nRelationships:")
        for rel in graph.relationships:
            print(f"  - {rel}")
    else:
        print("No graph data was generated from the text.")
#%%
print_graphs(graph_documents)

#%%

doc_path = "/home/a/Documents/asp/artfacts/Ontology-Guided Query Expansion for Biomedical Document Retrieval using Large Language Models.txt"

with open(doc_path, "r") as f:
    doc_text = f.read()
    
doc = Document(page_content=doc_text)

#%%
graph_docs_full = extract_graph(llm, doc)
#%%
print_graphs(graph_docs_full)



#%%

raw_text = """
Effective Question Answering (QA) on large biomedical document
collections requires effective document retrieval techniques. The latter
remains a challenging task due to the domain-specific vocabulary and
semantic ambiguity in user queries. We propose BMQExpander, a novel
ontology-aware query expansion pipeline that combines medical knowledge
– definitions and relationships – from the UMLS Metathesaurus with the
generative capabilities of large language models (LLMs) to enhance
retrieval effectiveness.

We implemented several state-of-the-art baselines, including sparse and
dense retrievers, query expansion methods, and biomedical-specific
solutions. We show that BMQExpander has superior retrieval performance
on three popular biomedical Information Retrieval (IR) benchmarks:
NFCorpus, TREC-COVID, and SciFact – with improvements of up to 22.1% in
NDCG@10 over sparse baselines and up to 6.5% over the strongest
baseline. Further, BMQExpander generalizes robustly under query
perturbation settings, in contrast to supervised baselines, achieving up
to 15.7% improvement over the strongest baseline. As a side
contribution, we publish our paraphrased benchmarks. Finally, our
qualitative analysis shows that BMQExpander has fewer hallucinations
compared to other LLM-based query expansion baselines.
"""

doc = Document(page_content=raw_text)

#%%

graph_docs_full = extract_graph(llm, doc)

#%%
print_graphs(graph_docs_full) 
