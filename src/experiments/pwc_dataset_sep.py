
from datasets import load_dataset
from huggingface_hub import login
from datasets import Dataset
import pandas as pd
import json
import os
# import myenv
from src.units.myenv import env
#%%
# huggingface login using python
hf_token = os.getenv("HUGGINGFACE_TOKEN")
login(hf_token)
#%%
# Login using e.g. `huggingface-cli login` to access this dataset
ds = load_dataset("pwc-archive/papers-with-abstracts")
ds
"""
DatasetDict({
    train: Dataset({
        features: ['paper_url', 'arxiv_id', 'nips_id', 'openreview_id', 'title', 'abstract', 'short_abstract', 'url_abs', 'url_pdf', 'proceeding', 'authors', 'tasks', 'date', 'conference_url_abs', 'conference_url_pdf', 'conference', 'reproduces_paper', 'methods'],
        num_rows: 576261
    })
})
"""

#%%
type(ds)
#%%

# Login using e.g. `huggingface-cli login` to access this dataset
ds1 = load_dataset("pwc-archive/links-between-paper-and-code")
ds1
"""
DatasetDict({
    train: Dataset({
        features: ['paper_url', 'paper_title', 'paper_arxiv_id', 'paper_url_abs', 'paper_url_pdf', 'repo_url', 'is_official', 'mentioned_in_paper', 'mentioned_in_github', 'framework'],
        num_rows: 300161
    })
})
"""

#%%
from tqdm import tqdm
# Merge the two datasets on arXiv id fields: `arxiv_id` from papers-with-abstracts
# and `paper_arxiv_id` from links-between-paper-and-code.
# Memory-efficient streaming join without loading entire datasets into RAM.
# Strategy: build a lookup from the (smaller) links dataset in memory,
# then stream over the papers dataset and write matching merged records
# to a JSONL file. Finally load the resulting JSONL as a HuggingFace Dataset.
#%%
# Build lookup from links dataset (paper_arxiv_id -> list of link rows)
links_map = {}
for row in tqdm(ds1['train'], desc="Building links map"):
    key = row.get('paper_arxiv_id')
    if key is None:
        continue
    links_map.setdefault(key, []).append(row)
#%%


#%%
# Stream over papers and write matches to separate JSON files to avoid holding merged data in memory
out_dir = 'merged_papers_links'
file_limit = 10000
os.makedirs(out_dir, exist_ok=True)

file_count = 0
for paper in tqdm(ds['train'].to_iterable_dataset(), desc="Merging datasets"):
    if file_count >= file_limit:
        break
    arxiv = paper.get('arxiv_id')
    if not arxiv:
        continue
    links = links_map.get(arxiv)
    if not links:
        continue
    for link in links:
        if file_count >= file_limit:
            break
        merged = dict(paper)
        for k, v in link.items():
            merged[f'{k}_link'] = v
        file_path = os.path.join(out_dir, f'merged_paper_link_{file_count:06d}.json')
        with open(file_path, 'w', encoding='utf-8') as fd:
            json.dump(merged, fd, default=str)
        file_count += 1

print(f"Saved {file_count} merged JSON files to {out_dir}")

#%%

# Load merged dataset from individual JSON files written to out_dir
# Use pandas -> Dataset to avoid json loader schema casting issues
records = []
json_files = sorted([f for f in os.listdir(out_dir) if f.endswith('.json')])
for fname in tqdm(json_files, desc="Loading merged JSON files"):
    path = os.path.join(out_dir, fname)
    try:
        with open(path, 'r', encoding='utf-8') as fd:
            records.append(json.load(fd))
    except Exception:
        continue

len(records)
#%%

if records:
    merged_df = pd.DataFrame.from_records(records)
    merged_ds = Dataset.from_pandas(merged_df)
    print(f"Loaded merged dataset with {len(merged_ds)} examples")
else:
    merged_ds = Dataset.from_pandas(pd.DataFrame())
    print("No records found in merged JSON files")

len(merged_ds)
#%%

fields = [
    # 'paper_url',
    'arxiv_id',
    'title',
    'abstract',
    'tasks',
    'reproduces_paper',
    'methods',
    # 'mentioned_in_paper_link',
    # 'mentioned_in_github_link',
    'framework_link',
]

n = min(file_limit, len(merged_ds)) if len(merged_ds) > 0 else 0
if n > 0:
    df_n = merged_ds.to_pandas()[fields].head(n)
else:
    df_n = pd.DataFrame(columns=fields)

print(f"Created pd.DataFrame with {len(df_n)} records")
print(df_n.head())

#%%
df_n.head()
#%%
# print all fields, dont omit anyting behind "...". Head
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
#%%
# Filter those where there are "methods" not []
df_filtered = df_n[df_n['methods'].notnull() & df_n['methods'].apply(lambda x: len(x) > 0)]
df_filtered.head()
#%%
# to csv
snippet_csv_path = 'data/merged_snippet1.csv'
df_filtered.to_csv(snippet_csv_path, index=False)
#%%
print(merged_ds)
