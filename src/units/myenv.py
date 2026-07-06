import os
from dotenv import dotenv_values
from src.models.dotdict import DotDict

# def get_default_env_path():
#     """Determines the default .env path based on the project structure."""
#     # Assumes this file is in src/units, so project root is two levels up.
#     project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
#     return os.path.join(project_root, '.env')

def load_env_to_dotdict(dotenv_path=".env"):
    """
    Loads variables from a .env file into a DotDict.

    Args:
        dotenv_path (str, optional): The path to the .env file.
                                     Defaults to the .env file in the project root.

    Returns:
        DotDict: A DotDict object containing the environment variables.
    """
    # if dotenv_path is None:
    #     dotenv_path = get_default_env_path()

    if not os.path.exists(dotenv_path):
        print(f"Warning: .env file not found at {dotenv_path}. No environment variables loaded.")
        return DotDict({})

    # Use dotenv_values to read the .env file into a dictionary
    # without polluting os.environ.
    env_dict = dotenv_values(dotenv_path)

    # Return as a DotDict
    return DotDict(env_dict)

# Create a globally accessible instance loaded from the default .env path.
# This gets executed once when the module is first imported.
env = myenv = load_env_to_dotdict()

for key, value in env.items():
    os.environ[key] = value

# --- Example Usage ---
if __name__ == "__main__":
    print("--- Loaded environment from default .env path ---")
    for key, value in env.items():
        print(f"  - {key}: {value}")