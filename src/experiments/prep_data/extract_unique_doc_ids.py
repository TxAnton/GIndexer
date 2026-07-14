import os
from tqdm import tqdm

def extract_unique_ids_from_qrel(input_path, output_path):
    """
    Reads a .qrel file to extract all unique document IDs and saves them
    to an output file.

    The function processes the file line by line for memory efficiency.

    Args:
        input_path (str): The path to the source .qrel file.
        output_path (str): The path to save the unique document IDs.
    """
    print(f"Extracting unique document IDs from {input_path}...")
    unique_doc_ids = set()

    try:
        # First, get the total number of lines for a nice progress bar
        with open(input_path, 'r') as f:
            total_lines = sum(1 for _ in f)

        # Process the file to extract doc IDs
        with open(input_path, 'r') as f:
            for line in tqdm(f, total=total_lines, desc="Parsing QREL", unit="lines"):
                parts = line.strip().split()
                if len(parts) == 4:
                    doc_id = parts[2]
                    unique_doc_ids.add(doc_id)

        # Ensure the output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        # Write the unique IDs to the output file
        print(f"\nFound {len(unique_doc_ids)} unique document IDs. Writing to {output_path}...")
        with open(output_path, 'w') as f:
            for doc_id in sorted(list(unique_doc_ids)):
                f.write(doc_id + '\n')

        print("Successfully saved unique document IDs.")

    except FileNotFoundError:
        print(f"Error: Input file not found at {input_path}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    # Using relative paths within the project structure
    QREL_INPUT_PATH = "data/Explicit_Semantic_Ranking_Dataset/s2.qrel"
    UNIQUE_IDS_OUTPUT_PATH = "data/unique_doc_ids.txt"

    extract_unique_ids_from_qrel(QREL_INPUT_PATH, UNIQUE_IDS_OUTPUT_PATH)
