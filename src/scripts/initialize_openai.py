import openai
from src.units.myenv import env as myenv
import os

def initialize_openai():
    """
    Initializes the OpenAI client using configuration from the global 'env' object.

    The 'env' object is expected to be loaded by the 'myenv' unit from a .env file.

    Returns:
        openai.OpenAI: An initialized OpenAI client instance, or None if configuration is missing.
    """
    # Get credentials from the globally loaded environment object
    api_key = os.getenv("OPENAI_API_KEY")
    api_base = os.getenv("OPENAI_API_BASE")
    model = os.getenv("OPENAI_MODEL")

    # Check if a valid API key is present
    if not api_key or api_key == "YOUR_API_KEY":
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("!!! WARNING: OPENAI_API_KEY is not set or is a placeholder in your .env file. !!!")
        print("!!! The OpenAI client will not be able to authenticate.                       !!!")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        return None

    # Initialize and return the OpenAI client
    try:
        client = openai.OpenAI(
            api_key=api_key,
            base_url=api_base, # Corresponds to the endpoint
        )
        print("OpenAI client initialized successfully!")
        if model:
            print(f"  - Default model from env: {model}")
        return client
    except Exception as e:
        print(f"Error initializing OpenAI client: {e}")
        return None

if __name__ == "__main__":
    print("Attempting to initialize OpenAI client using the 'myenv' unit...")
    openai_client = initialize_openai()

    if openai_client:
        print("\nThis script can be imported to get an initialized OpenAI client.")
        print("It now uses the centralized 'myenv' unit for configuration.")
        print("Example usage in another script:")
        print("  from src.scripts.initialize_openai import initialize_openai")
        print("  client = initialize_openai()")
