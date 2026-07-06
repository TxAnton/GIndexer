
from datasets import load_dataset
from huggingface_hub import login
from datasets import Dataset
import pandas as pd
import json
import os
# import myenv
from src.units.myenv import env as myenv
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

# Merge the two datasets on arXiv id fields: `arxiv_id` from papers-with-abstracts
# and `paper_arxiv_id` from links-between-paper-and-code.
# Memory-efficient streaming join without loading entire datasets into RAM.
# Strategy: build a lookup from the (smaller) links dataset in memory,
# then stream over the papers dataset and write matching merged records
# to a JSONL file. Finally load the resulting JSONL as a HuggingFace Dataset.
#%%
# Build lookup from links dataset (paper_arxiv_id -> list of link rows)
links_map = {}
for row in ds1['train']:
    key = row.get('paper_arxiv_id')
    if key is None:
        continue
    links_map.setdefault(key, []).append(row)
#%%

from tqdm import tqdm
#%%
# Stream over papers and write matches to JSONL to avoid holding merged data in memory
out_path = 'merged_papers_links.jsonl'
with open(out_path, 'w', encoding='utf-8') as fd:
    for paper in tqdm(ds['train'].to_iterable_dataset(), desc="Merging datasets"):
        arxiv = paper.get('arxiv_id')
        if not arxiv:
            continue
        links = links_map.get(arxiv)
        if not links:
            continue
        for link in links:
            # Merge dictionaries; suffix link fields to avoid collisions
            merged = dict(paper)
            for k, v in link.items():
                merged[f'{k}_link'] = v
            fd.write(json.dumps(merged, default=str) + '\n')

#%%

# Load merged dataset from JSONL
# Use pandas -> Dataset to avoid json loader schema casting issues
records = []
with open(out_path, 'r', encoding='utf-8') as fd:
    for line in tqdm(fd, desc="Loading merged JSONL"):
        try:
            records.append(json.loads(line))
        except Exception:
            continue
if records:
    merged_df = pd.DataFrame.from_records(records)
    merged_ds = Dataset.from_pandas(merged_df)
    print(f"Loaded merged dataset with {len(merged_ds)} examples")
else:
    merged_ds = Dataset.from_pandas(pd.DataFrame())
    print("No records found in merged JSONL")

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

n = min(1000, len(merged_ds)) if len(merged_ds) > 0 else 0
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
snippet_csv_path = 'data/merged_snippet.csv'
df_filtered.to_csv(snippet_csv_path, index=False)
#%%
print(merged_ds)
