import json
import os
from tqdm import tqdm

def split_jsonl_to_files(input_path, output_dir):
    """
    Reads a large JSON Lines file and splits each line into a separate
    JSON file in the specified output directory.

    This function is memory-efficient as it processes the file line by line.

    Args:
        input_path (str): Path to the input JSON Lines file (e.g., 's2_doc.json').
        output_dir (str): Directory where individual JSON files will be saved.
    """
    print(f"Starting to split {input_path} into individual files in {output_dir}...")

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    try:
        # First, count total lines for the progress bar without loading the file
        print("Counting lines in the input file...")
        with open(input_path, 'r') as f:
            total_lines = sum(1 for line in f)
        print(f"Found {total_lines} documents.")

        # Now, process the file and save each line
        with open(input_path, 'r') as f:
            for line in tqdm(f, total=total_lines, desc="Processing documents", unit="doc"):
                try:
                    data = json.loads(line)
                    doc_id = data.get('docno')

                    if not doc_id:
                        print(f"Warning: Skipping a line as it has no 'docno'. Content: {line[:100]}...")
                        continue

                    # Sanitize doc_id to make it a valid filename if needed, though they look safe
                    filename = f"{doc_id}.json"
                    output_path = os.path.join(output_dir, filename)

                    with open(output_path, 'w') as out_f:
                        json.dump(data, out_f, indent=4)

                except json.JSONDecodeError:
                    print(f"Warning: Skipping a line due to JSON decode error. Content: {line[:100]}...")
                    continue

    except FileNotFoundError:
        print(f"Error: Input file not found at {input_path}")
        return
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return

    print(f"\nProcessing complete. All documents have been saved to {output_dir}")

if __name__ == "__main__":

    INPUT_JSONL = "data/Explicit_Semantic_Ranking_Dataset/s2_doc.json"
    OUTPUT_DIRECTORY = "data/s2_docs"

    split_jsonl_to_files(INPUT_JSONL, OUTPUT_DIRECTORY)
