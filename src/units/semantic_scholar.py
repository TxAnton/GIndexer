import requests
import time
import os
from src.units.myenv import env as myenv

class SemanticScholar:
    """
    A class to interact with the Semantic Scholar Graph API.
    Provides methods to fetch paper details, with optional API key support.
    """
    BASE_URL = 'https://api.semanticscholar.org/graph/v1'

    def __init__(self, api_key=None, delay=2):
        """
        Initializes the SemanticScholar client.

        Args:
            api_key (str, optional): Your Semantic Scholar API key.
                                     Provides a higher rate limit.
            delay (int, optional): Delay in seconds between requests to avoid rate limiting.
        """
        self.headers = {}
        if api_key:
            self.headers['x-api-key'] = api_key
            print("Semantic Scholar client initialized with an API key.")
        else:
            print("Semantic Scholar client initialized without an API key.")
        self.delay = delay

    def get_paper_by_id(self, paper_id, retries=20, fields=None):
        """
        Fetches information for a single paper by its ID.

        Args:
            paper_id (str): The ID of the paper to fetch.
            fields (list[str], optional): A list of fields to retrieve.
                                          Defaults to ['title', 'year', 'authors'].

        Returns:
            dict: The JSON response from the API, or None if the request fails.
        """
        if fields is None:
            fields = ["title", "year", "authors", "openAccessPdf"]
            

        url = f"{self.BASE_URL}/paper/{paper_id}"
        params = {"fields": ",".join(fields)}

        #  only retry on http error 429
        while retries > 0:
            try:
                response = requests.get(url, headers=self.headers, params=params)
                response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
                return response.json()
            except requests.exceptions.HTTPError as http_err:
                if response.status_code == 429:
                    print("Rate limit exceeded. Retrying...")
                    time.sleep(self.delay)  # Wait before retrying
                    retries -= 1
                    continue
                print(f"HTTP error occurred: {http_err}")
                print(f"Response content: {response.text}")
            except requests.exceptions.RequestException as req_err:
                print(f"An error occurred: {req_err}")
            break  # Exit the loop if not a rate limit error
        print(f"Failed to fetch paper data after {retries} retries.")

        return None


