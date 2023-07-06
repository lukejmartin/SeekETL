import pytest
from bs4 import BeautifulSoup
from extract.scraper import WebScraper, Category, Theme, Industry


@pytest.fixture
def mock_html_themes():
    return '<html><body><div name="browseByThemes"><a class="_1frdw130" href="/theme1">Theme 1</a><a class="_1frdw130" href="/theme2">Theme 2</a></div></body></html>'

@pytest.fixture
def mock_html_industries():
    return '<html><body><div name="BROWSE_BY_INDUSTRIES"><a class="_1frdw130" href="/industry1">Industry 1</a><a class="_1frdw130" href="/industry2">Industry 2</a></div></body></html>'

@pytest.fixture
def mock_soup_themes(mock_html_themes):
    return BeautifulSoup(mock_html_themes, 'html.parser')

@pytest.fixture
def mock_soup_industries(mock_html_industries):
    return BeautifulSoup(mock_html_industries, 'html.parser')

def test_get_themes(mock_soup_themes):
    scraper = WebScraper()
    themes = scraper.get_themes(mock_soup_themes)
    assert isinstance(themes, list)
    assert len(themes) == 2
    assert isinstance(themes[0], Theme)
    assert themes[0].title == 'Theme 1'
    assert themes[0].url == 'https://www.seek.com.au/theme1'

def test_get_industries(mock_soup_industries):
    scraper = WebScraper()
    industries = scraper.get_industries(mock_soup_industries)
    assert isinstance(industries, list)
    assert len(industries) == 2
    assert isinstance(industries[0], Industry)
    assert industries[0].title == 'Industry 1'
    assert industries[0].url == 'https://www.seek.com.au/industry1'

def test_get_job_ids():
    mock_html = """
    <html>
        <body>
            <a data-analytics-action="Click - Role card" href="/electrical-engineer">Electrical Engineer</a>
            <a data-analytics-action="Click - Role card" href="/civil-engineer">Civil Engineer</a>
            <a data-analytics-action="Click - Role card" href="/mechanical-engineer">Mechanical Engineer</a>
        </body>
    </html>
    """
    soup = BeautifulSoup(mock_html, 'html.parser')

    industry = Industry(title='Engineering', url='https://www.seek.com.au/explore-careers/engineering')
    industry.get_job_ids(soup)

    assert len(industry.job_ids) == 3
    assert isinstance(industry.job_ids, list)
    assert industry.job_ids == ['electrical-engineer', 'civil-engineer', 'mechanical-engineer']

def test_get_job_ids_not_found_error():
    mock_html = """
    <html>
        <body>
            <a data-analytics-action="INVALID MESSAGE" href="/electrical-engineer">Electrical Engineer</a>
            <a data-analytics-action="INVALID MESSAGE" href="/civil-engineer">Civil Engineer</a>
            <a data-analytics-action="INVALID MESSAGE" href="/mechanical-engineer">Mechanical Engineer</a>
        </body>
    </html>
    """
    soup = BeautifulSoup(mock_html, 'html.parser')
    industry = Industry(title='Engineering', url='https://www.seek.com.au/explore-careers/engineering')

    with pytest.raises(ValueError):
        industry.get_job_ids(soup)

