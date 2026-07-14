
import os
from pathlib import Path
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document
from langchain_experimental.graph_transformers import LLMGraphTransformer
from src.units.myenv import env as myenv

class GraphExtractor:
    """
    A class to handle the initialization of a language model and the
    extraction of graph structures from text documents.
    """

    def __init__(self, api_key=None, base_url=None, model=None):
        """
        Initializes the language model.
        It uses credentials from the `myenv` unit by default but can be
        overridden with specific arguments.

        Args:
            api_key (str, optional): OpenAI API key. Defaults to env.OPENAI_API_KEY.
            base_url (str, optional): OpenAI API base URL. Defaults to env.OPENAI_API_BASE.
            model (str, optional): The model to use. Defaults to env.OPENAI_MODEL.
        """
        self.api_key = api_key or myenv.get("OPENAI_API_KEY")
        self.base_url = base_url or myenv.get("OPENAI_API_BASE")
        self.model = model or myenv.get("OPENAI_MODEL")
        self.cache_dir = Path(myenv.get("GRAPH_CACHE_DIR", "data/graph_cache"))
        self.cache = {}  # Simple in-memory cache for extracted graphs
        self.verbose = os.getenv("VERBOSE", "False").lower() in ("true", "1", "t")

        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
            print(f"Created cache directory at {self.cache_dir}")
        elif (self.cache_dir / "graph_cache.pkl").exists():
                print(f"Loading existing cache from {self.cache_dir / 'graph_cache.pkl'}")
                self.load_cache()


        if not self.api_key or self.api_key == "YOUR_API_KEY":
            raise ValueError("OpenAI API key is not configured. Please set it in your .env file.")

        self.llm = ChatOpenAI(
            model=self.model,
            api_key=self.api_key,
            base_url=self.base_url,
            temperature=0
        )
        print("LLM Initialized successfully.")
        print(f"  - Model: {self.model}")
        print(f"  - Endpoint: {self.base_url}")


    def load_cache(self):
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        cache_file = self.cache_dir / "graph_cache.pkl"
        if cache_file.exists():
            with cache_file.open("rb") as f:
                import pickle
                return pickle.load(f)
        

    def save_cache(self):
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        cache_file = self.cache_dir / "graph_cache.pkl"
        with cache_file.open("wb") as f:
            import pickle
            pickle.dump(self.cache, f)
        

    def extract_graph(self, doc, allowed_nodes=None, allowed_relationships=None, **kwargs):
        """
        Processes a Document object and converts it into a graph structure.
        If allowed_nodes and allowed_relationships are None, no restrictions are placed.

        Args:
            doc (Document): The LangChain Document object containing the text.
            allowed_nodes (list[str], optional): A list of node types to allow.
            allowed_relationships (list[str], optional): A list of relationship types to allow.

        Returns:
            list[GraphDocument]: A list containing the extracted graph data.
        """
        cache_key = (doc.page_content, tuple(allowed_nodes or []), tuple(allowed_relationships or []))
        if cache_key in self.cache:
            if self.verbose:
                print("Returning cached graph...")
            return self.cache[cache_key]

        
        if self.verbose:
            print("\nExtracting graph from document...")
        llm_transformer = LLMGraphTransformer(
            llm=self.llm,
            allowed_nodes=allowed_nodes,
            allowed_relationships=allowed_relationships,
            **kwargs
        )
        graph_docs = llm_transformer.convert_to_graph_documents([doc])
        self.cache[cache_key] = graph_docs  # Cache the result
        if self.verbose:
            print("Graph extraction complete.")
        return graph_docs

    @staticmethod
    def print_graphs(graph_documents):
        """
        Prints the nodes and relationships from a list of GraphDocument objects.

        Args:
            graph_documents (list[GraphDocument]): The graph documents to print.
        """
        if not graph_documents:
            print("No graph data was generated from the text.")
            return

        print("\n--- Output Graph ---")
        for graph_doc in graph_documents:
            print("Nodes:")
            for node in graph_doc.nodes:
                print(f"  - {node}")

            print("\nRelationships:")
            for rel in graph_doc.relationships:
                print(f"  - {rel}")
        print("--------------------\n")

