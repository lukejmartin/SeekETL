"""
Handles the API requests.
"""

import json
import requests
from requests.exceptions import RequestException
from scraper import export_json
import time
from config import url, payload, headers  # Secret parameters
from tqdm import tqdm
import os

def main():
    fetch_all(
        filepath='data/themes.json',
        url=url,
        payload=payload,
        headers=headers,
        by='themes'
    )


def load_json(filepath: str) -> dict:
    """Import json file to dictionary."""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        return data
    
    except FileNotFoundError as e:
        print(e)


def call_api(jobs_list: list[str], url: str,
             payload: dict, headers: dict) -> dict:
    """Get response from graph ql query."""
    payload['variables']['aliases'] = jobs_list  # Updates the query parameters.

    try:
        response = requests.request('POST', url=url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()

    except RequestException as e:
        raise RuntimeError(f'API request error: {e}')


def fetch_all(filepath: str, url: str, payload: dict,
              headers: dict, by: str, sleep: int = 5) -> None:
    """Iterate over themes/industries and export to json file(s)."""

    if by not in ['themes', 'industries']:
        raise ValueError(f'Invalid parameter: {by}. Enter either "industries" or "themes."')

    categories = load_json(filepath)
    
    for category, jobs_list in tqdm(categories.items()):
        data = call_api(jobs_list=jobs_list, url=url, payload=payload, headers=headers)

        filepath = f'data/{by}/{category.replace(" ", "-").lower()}.json'  # Modify category name to snake-case.
        export_json(data=data, filepath=filepath)
        time.sleep(sleep)


if __name__ == "__main__":
    main()
