import json
from pathlib import Path
#%%
# --- DATA PATHS ---
PER_REQ_DIR = Path("data/per_req")
S2_DOCS_DIR = Path("data/s2_docs")
OUTPUT_PATH = Path("data/missing_docs.json")
#%%

def load_query_ids() -> list[str]:
    if not PER_REQ_DIR.exists():
        return []

    query_files = sorted(PER_REQ_DIR.glob("*.txt"))
    return [query_file.stem for query_file in query_files]


def load_doc_ids(query_file: Path) -> list[str]:
    with query_file.open("r", encoding="utf-8") as handle:
        return [line.strip() for line in handle if line.strip()]


def find_missing_docs(query_id: str, doc_ids: list[str]) -> list[str]:
    missing_docs = []
    for doc_id in doc_ids:
        doc_path = S2_DOCS_DIR / f"{doc_id}.json"
        if not doc_path.exists():
            missing_docs.append(doc_id)
    return missing_docs

#%%

query_ids = load_query_ids()

if not query_ids:
    print(f"No query files found in {PER_REQ_DIR}.")
    exit(1)

missing_docs_by_query: dict[int, list[str]] = {}

for query_id in query_ids:
    query_file = PER_REQ_DIR / f"{query_id}.txt"
    if not query_file.exists():
        continue

    doc_ids = load_doc_ids(query_file)
    missing_docs = find_missing_docs(query_id, doc_ids)
    missing_docs_by_query[int(query_id)] = missing_docs
    
# print x/y queries have missing docs
total_queries = len(query_ids)
queries_with_missing_docs = sum(1 for docs in missing_docs_by_query.values() if docs)
print(f"Found {queries_with_missing_docs}/{total_queries} queries with missing documents.")
#%%
# OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
with OUTPUT_PATH.open("w", encoding="utf-8") as fd:
    json.dump(dict(sorted(missing_docs_by_query.items())), fd, indent=2)

print(f"Processed {len(query_ids)} query files.")
missing_count = sum(len(doc_ids) for doc_ids in missing_docs_by_query.values())
print(f"Saved missing document report to {OUTPUT_PATH}")
print(f"Found {missing_count} missing document references.")

#%%

# missing abstracts
missing_abstracts_by_query: dict[int, list[str]] = {}

for query_id in query_ids:
    query_file = PER_REQ_DIR / f"{query_id}.txt"
    if not query_file.exists():
        continue

    doc_ids = load_doc_ids(query_file)
    missing_abstracts = []
    
    for doc_id in doc_ids:
        doc_path = S2_DOCS_DIR / f"{doc_id}.json"
        if doc_path.exists():
            with doc_path.open("r", encoding="utf-8") as handle:
                doc_data = json.load(handle)
                if not doc_data.get("paperAbstract") or len(doc_data.get("paperAbstract")) == 0 or len(doc_data.get("paperAbstract")[0]) <=2 :
                    missing_abstracts.append(doc_id)
    
    if missing_abstracts:
        missing_abstracts_by_query[int(query_id)] = missing_abstracts
    else:
        missing_abstracts_by_query[int(query_id)] = []

total_queries = len(query_ids)
queries_with_missing_abstracts = sum(1 for docs in missing_abstracts_by_query.values() if docs)
print(f"Found {queries_with_missing_abstracts}/{total_queries} queries with missing abstracts.")

# queries with no missing abstracts
queries_with_no_missing_abstracts = [qid for qid, docs in missing_abstracts_by_query.items() if not docs]
print(f"Queries with no missing abstracts: {queries_with_no_missing_abstracts}")

#%%

#  missing abstracts per query sorted descending by count
sorted_missing_abstracts = sorted(missing_abstracts_by_query.items(), key=lambda x: len(x[1]), reverse=True)
print("Missing abstracts per query (sorted by count):")
for query_id, docs in sorted_missing_abstracts:
    print(f"Query {query_id}: {len(docs)} missing abstracts")   

#%%
# Top n queries with the least missing abstracts, with query number 51 or above, with the number of missing abstracts

n = 6
top_n_queries = sorted(((qid, docs) for qid, docs in missing_abstracts_by_query.items() if qid >= 51), key=lambda x: len(x[1]))
print(f"Top {n} queries with the least missing abstracts (query ID >= 51):")
for query_id, docs in top_n_queries[:n]:
    print(f"Query {query_id}: {len(docs)} missing abstracts")

# as list of query IDs only
print(f"Top {n} queries with the least missing abstracts (query ID >= 51): {[qid for qid, docs in top_n_queries[:n]]}")

# top_n_queries = [qid for qid, docs in sorted_missing_abstracts if qid >= 51][:n]
# print(f"Top {n} queries with the least missing abstracts (query number >= 51): {top_n_queries}")

#%%
#%%
abstracts_output_path = Path("data/missing_abstracts.json")
with abstracts_output_path.open("w", encoding="utf-8") as fd:
    json.dump(dict(sorted(missing_abstracts_by_query.items())), fd, indent=2)

abstracts_count = sum(len(doc_ids) for doc_ids in missing_abstracts_by_query.values())
print(f"Saved missing abstracts report to {abstracts_output_path}")
print(f"Found {abstracts_count} missing abstracts.")



        
