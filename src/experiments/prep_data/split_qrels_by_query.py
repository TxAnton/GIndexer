import os
from tqdm import tqdm
from src.units.parsers import parse_qrel_file

def group_and_save_docs_by_query(qrel_path, output_dir):
    """
    Parses a .qrel file and saves the documents for each query into
    separate files within the specified output directory.

    Args:
        qrel_path (str): The path to the source .qrel file.
        output_dir (str): The directory where query-specific files will be saved.
    """
    # 1. Parse the entire QREL file into a dictionary
    # This is efficient as it reads the file once.
    relevance_data = parse_qrel_file(qrel_path)
    if not relevance_data:
        print("Parsing failed. Aborting script.")
        return

    # 2. Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    print(f"\nSaving documents per query to {output_dir}...")

    # 3. Iterate through each query and save its documents
    for query_id, doc_judgments in tqdm(relevance_data.items(), desc="Saving query files"):
        output_filename = os.path.join(output_dir, f"{query_id}.txt")

        # Get a list of all document IDs for the current query
        doc_ids = doc_judgments.keys()

        with open(output_filename, 'w') as f:
            for doc_id in sorted(list(doc_ids)):
                f.write(doc_id + '\n')

    print(f"\nProcessing complete. All queries have been saved to separate files in {output_dir}.")

if __name__ == "__main__":
    # Define paths based on the project structure
    QREL_INPUT_PATH = "data/Explicit_Semantic_Ranking_Dataset/s2.qrel"
    PER_QUERY_OUTPUT_DIR = "data/per_req"

    group_and_save_docs_by_query(QREL_INPUT_PATH, PER_QUERY_OUTPUT_DIR)
