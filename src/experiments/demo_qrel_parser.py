from src.units.parsers import parse_qrel_file
#%%

"""
Demonstrates how to use the qrel parser unit to load and inspect
relevance judgments.
"""
#%%
# Define the path to the ground truth file
qrel_file_path = "/home/a/Documents/asp/artfacts/data/Explicit_Semantic_Ranking_Dataset_short/s2.qrel"
#%%
# Use the parsing function from our new unit
relevance_data = parse_qrel_file(qrel_file_path)

if not relevance_data:
    print("\nDemo finished: No data was parsed.")

#%%

# --- How to use the parsed data ---
print("\n--- Inspecting the Parsed Data ---")

# 1. Get a list of all query IDs
all_query_ids = list(relevance_data.keys())
print(f"Total number of queries with judgments: {len(all_query_ids)}")
print(f"First 5 query IDs: {all_query_ids[:5]}")

# 2. Look up judgments for a specific query
sample_query_id = '1'
if sample_query_id in relevance_data:
    query_judgments = relevance_data[sample_query_id]
    print(f"\nNumber of judged documents for query '{sample_query_id}': {len(query_judgments)}")

    # 3. Check the relevance of a specific document for that query
    sample_doc_id = '373f76633cc1f6c7a421e31c989842021a52fca4'
    if sample_doc_id in query_judgments:
        score = query_judgments[sample_doc_id]
        print(f"  - The relevance score for doc '{sample_doc_id}' is: {score}")
    else:
        print(f"  - Document '{sample_doc_id}' was not judged for this query.")

print("\n--- Demo finished ---")
