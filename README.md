# GIndexer: Semantic Technology Experiments

README is ai generated

This project is a workspace for developing and experimenting with semantic technologies in Python. It includes tools for data processing, graph extraction from text, interaction with academic search APIs, and connecting to graph databases.

## Project Structure

The repository is organized into data, source code, and configuration files.

```
.project-root/
├── data/                 # Raw and processed data files.
│   ├── s2_docs/          # Individual paper JSON files, split from the main dataset.
│   └── sample_text.txt   # A small text file for quick demos.
├── src/                  # All Python source code.
│   ├── experiments/      # Standalone scripts for experiments and demos.
│   │   └── prep_data/    # Scripts for data preprocessing.
│   ├── models/           # Core data structures, like DotDict.
│   ├── scripts/          # Reusable scripts, e.g., client initializers.
│   ├── units/            # Core, reusable components (API clients, parsers).
│   └── utils/            # Utility functions.
├── .env                  # Local environment variables (API keys, credentials).
├── pyproject.toml        # Project metadata and build configuration.
├── requirements.txt      # Python package dependencies.
└── README.md             # This file.
```

## Getting Started

### 1. Environment Setup

Before running any scripts, you need to configure your local environment.

**Create an Environment File:**

Copy the example `.env.example` to a new file named `.env` and fill in your credentials.

```bash
cp .env.example .env
```

This file is used to configure API clients and database connections. It is included in `.gitignore` and should not be committed.

**Install Dependencies:**

Install all required Python packages using pip:

```bash
pip install -r requirements.txt
```

### 2. Core Components (Units)

The `src/units/` directory contains the main reusable components of this project:

- **`myenv.py`**: A centralized module that loads all variables from the `.env` file into a globally accessible `env` object (`DotDict`). This is the standard way to manage configuration in this project.
- **`graph_extractor.py`**: Contains the `GraphExtractor` class, which uses LangChain and an OpenAI model to extract graph structures (nodes and relationships) from text documents.
- **`semantic_scholar.py`**: A `SemanticScholar` class that provides a client for interacting with the Semantic Scholar API to fetch paper details.
- **`parsers.py`**: Includes utility functions for parsing specific data formats, such as the `parse_qrel_file` function for TREC relevance-judgment files.

### 3. Experiments

The `src/experiments/` directory is for running standalone tests and demonstrations. These scripts are structured like IPython notebooks, using `#%%` to separate cells.

- **`demo_graph_extraction.py`**: Shows how to use the `GraphExtractor` to pull a graph from `data/sample_text.txt`.
- **`demo_semantic_scholar.py`**: Demonstrates fetching paper data in a loop using the `SemanticScholar` client.
- **`demo_qrel_parser.py`**: Explains how to parse and use the `s2.qrel` ground-truth relevance file.
- **`prep_data/split_s2_docs.py`**: A utility script to process the very large `s2_doc.json` file into individual JSON files, making it easier to work with.

### 4. Available Data

The project uses data from the **Explicit Semantic Ranking Dataset**.

- **`/home/a/Documents/asp/artfacts/data/Explicit_Semantic_Ranking_Dataset/`**: The main dataset directory, containing the source files for search queries (`s2_query.json`), document texts (`s2_doc.json`), and relevance judgments (`s2.qrel`).
- **`data/`**: The local data directory within this project.
- **`data/s2_docs/`**: The output of the `split_s2_docs.py` script. Contains one JSON file per paper, which is much more efficient for lookups.
