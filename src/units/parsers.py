import pandas as pd
from collections import defaultdict

def parse_qrel_file(file_path):
    """
    Parses a .qrel file into a dictionary for easy lookup.

    The .qrel file format is: query_id, iteration, doc_id, relevance_score

    Args:
        file_path (str): The path to the .qrel file.

    Returns:
        dict: A dictionary where keys are query IDs and values are
              another dictionary mapping doc_ids to their integer relevance scores.
              Example: { '1': { 'doc_a': 2, 'doc_b': 0 }, '2': { ... } }
    """
    print(f"Parsing .qrel file from: {file_path}")
    relevance_judgments = defaultdict(dict)

    try:
        with open(file_path, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) == 4:
                    query_id, _, doc_id, score = parts
                    relevance_judgments[query_id][doc_id] = int(score)
    except FileNotFoundError:
        print(f"Error: QREL file not found at {file_path}")
        return None

    print(f"Successfully parsed {len(relevance_judgments)} queries.")
    return dict(relevance_judgments)

if __name__ == '__main__':
    print("--- Demonstrating QREL Parser ---")
    qrel_path = "/home/a/Documents/asp/artfacts/data/Explicit_Semantic_Ranking_Dataset_short/s2.qrel"

    # Parse the file
    judgments = parse_qrel_file(qrel_path)

    # Display some results for demonstration
    if judgments:
        sample_query_id = list(judgments.keys())[0]
        print(f"\n--- Sample Judgments for Query ID: {sample_query_id} ---")

        sample_docs = list(judgments[sample_query_id].items())[:5]
        for doc_id, score in sample_docs:
            print(f"  - Document: {doc_id}, Relevance Score: {score}")

        # Example of how to look up a specific score
        first_doc_id = sample_docs[0][0]
        lookup_score = judgments[sample_query_id][first_doc_id]
        print(f"\nExample Lookup: Score for doc {first_doc_id} is {lookup_score}")
        print("---------------------------------")
