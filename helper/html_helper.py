from urllib import request
from urllib.error import HTTPError
from bs4 import BeautifulSoup


# ====================
def page_exists(url: str) -> bool:
    """Return True if a page exists at the given URL"""

    try:
        status_code = request.urlopen(url).getcode()
        if status_code == 200:
            return True
    except HTTPError:
        return False


# ====================
def get_bs(url: str) -> BeautifulSoup:
    """Get BeautifulSoup object from URL"""

    with request.urlopen(url) as response:
        html = response.read()
    bs = BeautifulSoup(html, 'html.parser')
    return bs


# ====================
def get_html(url: str) -> str:
    """Get HTML from URL"""

    html = request.urlopen(url).read()
    return html


# ====================
def bs_from_html(html: str) -> BeautifulSoup:
    """Get BeautifulSoup object from HTML"""

    bs = BeautifulSoup(html, 'html.parser')
    return bs


# ====================
def get_all_text(tag) -> str:
    """Get text from all tags contained in bs4 ResultSet"""

    return ''.join(
        [t.text.strip()
         for t in tag if not t.text.isspace()]
    )


# ====================
def get_all_link_urls(url: str) -> list:

    bs = get_bs(url)
    return [a['href'] for a in bs.find_all('a', href=True)]
