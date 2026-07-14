import os
from dotenv import dotenv_values
from src.models.dotdict import DotDict

def load_env_to_dotdict(dotenv_path=".env"):
    """
    Loads variables from a .env file into a DotDict.

    Args:
        dotenv_path (str, optional): The path to the .env file.
                                     Defaults to the .env file in the project root.

    Returns:
        DotDict: A DotDict object containing the environment variables.
    """

    if not os.path.exists(dotenv_path):
        print(f"Warning: .env file not found at {dotenv_path}. No environment variables loaded.")
        return DotDict({})

    env_dict = dotenv_values(dotenv_path)

    return DotDict(env_dict)

env = myenv = load_env_to_dotdict()

for key, value in env.items():
    os.environ[key] = value

if __name__ == "__main__":
    print("--- Loaded environment from default .env path ---")
    for key, value in env.items():
        print(f"  - {key}: {value}")