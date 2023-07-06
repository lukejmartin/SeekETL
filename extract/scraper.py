from bs4 import BeautifulSoup
import requests
from dataclasses import dataclass
import re
import time
import json
import os
from tqdm import tqdm


def main():
    soup = WebScraper.get_soup('https://www.seek.com.au/career-advice/explore-careers')
    scraper = WebScraper()
    extract_all_ids(by='theme', soup=soup, scraper=scraper)


@dataclass
class Category:
    title: str
    url: str

    def get_job_ids(self, soup: BeautifulSoup) -> None:
        """Extract job IDs, e.g. ['accountant', 'financial-analyst', 'software-engineer']"""
        # Pattern match the job title at the end of the URL string.
        extract_id = lambda url: re.search(r'[^/]+$', url).group(0)

        tags = soup.find_all(attrs={'data-analytics-action': 'Click - Role card'})    
        # If no tags are found.
        if not tags:
            raise ValueError('No job ids found with the specified attributes {"data-analytics-action"; "Click - Role card"}')

        self.job_ids = [extract_id(tag['href']) for tag in tags]

@dataclass
class Industry(Category):
    super


@dataclass 
class Theme(Category):
    super


class WebScraper:
    def __init__(self) -> None:
        self.base_url = 'https://www.seek.com.au'

    @staticmethod
    def get_soup(url: str) -> BeautifulSoup:
        """Return beautiful soup object from http request."""
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        return soup
    
    def _get_categories(self, soup: BeautifulSoup,
                        attr_name: str,
                        category: Category) -> list[Category]:
        """
        Parse soup object for categories (industries/themes) and return list of category objects.

        Parameters:
            soup: BeautifulSoup object of the main page.
            attr_name: Attribute name to search.
            category: Category object (either 'Theme' or 'Industry').

        Returns:
            List of Category objects.
        """
        try:
            tags = soup.find(attrs={'name': attr_name}).find_all(attrs={'class': '_1frdw130'})
            title = lambda tag: tag.get_text()
            url = lambda tag: self.base_url + tag['href']

            return [
                category(title=title(tag), url=url(tag))
                for tag in tags
            ]
        
        except AttributeError as e:
            print('Could not extract tags.')
            raise AttributeError
        
    def get_themes(self, soup: BeautifulSoup) -> list[Theme]:
        """Return list of theme objects."""
        return self._get_categories(soup=soup, attr_name='browseByThemes', category=Theme)
    
    def get_industries(self, soup: BeautifulSoup) -> list[Industry]:
        """Return list of industry objects."""
        return self._get_categories(soup=soup, attr_name='BROWSE_BY_INDUSTRIES', category=Industry)
    

def export_json(data: dict, filepath: str) -> None:
    """
    Export dictionary to json file.

    Parameters:
        data: Dictionary to export.
        filepath: Full filepath for the exported file.
    """
    directory = os.path.dirname(filepath)
    os.makedirs(directory, exist_ok=True)  # Create directories if they don't exist.

    with open(filepath, 'w') as f:
        json.dump(data, f)


def extract_all_ids(by: str, soup: BeautifulSoup,
                    scraper: WebScraper, sleep: int = 5) -> None:
    """
    Iterate over themes/industries and extract list of jobs IDs for each category.

    Parameters
        by: Sort by 'theme' or 'industry'.
        soup: BeautifulSoup object to parse.
        scraper: WebScraper.
        sleep [optional]: Wait time (secs) between loops.
    """
    if by not in ['theme', 'industry']:
        raise ValueError(f'Invalid parameter: {by}. Enter either "industry" or "theme."')

    data = {}
    if by == 'theme':
        try:
            themes = scraper.get_themes(soup)
            for theme in tqdm(themes):
                soup = WebScraper.get_soup(theme.url)
                theme.get_job_ids(soup)
                data[theme.title] = theme.job_ids
                time.sleep(sleep)
        finally:
            export_json(data=data, filepath='data/themes.json')
    
    elif by == 'industry':
        try:
            industries = scraper.get_industries(soup)
            for industry in tqdm(industries):
                soup = WebScraper.get_soup(industry.url)
                industry.get_job_ids(soup)
                data[industry.title] = industry.job_ids
                time.sleep(sleep)
        finally:
            export_json(data=data, filepath='data/industries.json')


if __name__ == "__main__":
    main()
