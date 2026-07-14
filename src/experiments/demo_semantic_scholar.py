import time
from tqdm import tqdm
from src.units.semantic_scholar import SemanticScholar
from src.units.myenv import env
#%%

"""
Demonstrates using the SemanticScholar unit to fetch paper details in a loop.
"""
# 1. Initialize the SemanticScholar client
# It uses the HUGGINGFACE_TOKEN from the .env file as the API key.
# Replace with a dedicated S2_API_KEY if you have one.
# s2_api_key = env.get("HUGGINGFACE_TOKEN") # Or another key like S2_API_KEY
s2_client = SemanticScholar(api_key=None, delay=2)
#%%
# 2. List of paper IDs to fetch
paper_ids = [
    # "arXiv:1706.03762",  # Attention Is All You Need
    # "arXiv:2303.12106",  # LLMGraphTransformer
    "649def34f8be52c8b66281af98ae884c09aef38b" # BERT
]
#%%
print(f"--- Starting to fetch {len(paper_ids)} papers ---")

# 3. Loop through IDs and fetch data
for paper_id in tqdm(paper_ids, desc="Fetching papers", unit="paper"):
    print(f"\nFetching details for paper: {paper_id}")
    paper_data = s2_client.get_paper_by_id(
        paper_id,
        retries=20,
        # fields=["title", "year", "authors.name"]
    )

    if paper_data:
        print(f"  -> Title: {paper_data.get('title')}")
        authors = [author['name'] for author in paper_data.get('authors', [])]
        print(f"  -> Authors: {authors}")
    else:
        print("  -> Failed to retrieve paper data.")

    # Wait for 2 seconds before the next request to respect rate limits
    print("Waiting 2 seconds...")
    time.sleep(2)

print("\n--- Demo finished ---")

