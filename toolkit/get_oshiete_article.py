"""
get_oshiete_article.py

Defines PageResult class for getting information from a Q&A page on the
website oshiete.goo.ne.jp.
"""

import bs4

from helper.file_helper import save_text_to_file
from helper.html_helper import get_all_text, get_bs

TEST_PAGE_URL = "https://oshiete.goo.ne.jp/qa/49186.html"
TEST_PAGE_YEAR = 2001


class PageResult:
    """
    A class to represent the result of scraping a Q&A page on the website
    oshiete.goo.ne.jp

    Attributes
    ----------

    success: bool
        whether the page was successfully scraped
    err_msg: str
        an error message in the case the page could not be scraped
    category: str
        the category of the article. This is the top-level category
        displayed immediately to the right of "教えて!goo" in the
        category list near the top of the page
    text: str
        the text from the question and all answers on the page that
        were written in the year specified, separated by \n\n.
        Does not include extra comments, thank yous etc.
    """

    def __init__(self, url: str, year: int):
        """
        Scrape the page and store the results in the attributes.

        Parameters
        ----------
        url: str
            The URL of the page to scrape.
            Has the form https://oshiete.goo.ne.jp/qa/<DIGITS>.html
        year: int
            The year for which to get text content from.
            No questions or answers that were not answered in this
            year will be included in the text attribute, and if no
            content written in the year is found 'success' will be set
            to False
        """

        # Get page HTML
        try:
            bs = get_bs(url)
        except Exception as e:
            self.success = False
            self.err_msg = f'<<<{e}>>> error while getting HTML.'
            return

        # Determine category
        try:
            self.category = get_main_category(bs)
        except Exception as e:
            self.success = False
            self.err_msg = f'<<<{e}>>> error while attempting to ' + \
                           'determine category.'
            return

        # Get text content from questions and answers
        try:
            self.text = get_all_q_and_a_text(bs, year)
        except Exception as e:
            self.success = False
            self.err_msg = f"<<<{e}>>> error while parsing!"
            return

        # Make sure there is some content to return
        if len(self.text) == 0 or self.text.isspace():
            self.success = False
            self.err_msg = f"Did not find any content written in {year}."
            return
        else:
            self.success = True
            return


# ====================
def get_main_category(bs: bs4.BeautifulSoup) -> str:
    """Get the top-level category from the page"""

    all_categories = bs.find(id='crumb')
    main_category = all_categories.findAll(name='a')[1].text
    return main_category


# ====================
def get_all_q_and_a_text(bs: bs4.BeautifulSoup, year: int) -> str:
    """Get the text from all questions and answers on the page that were
    written in the year specified"""

    qs_and_as = bs.findAll(name='div', class_=['q_article', 'a_article'])
    all_texts = [get_q_a_text(qa, year)
                 for qa in qs_and_as if get_q_a_text(qa, year)]
    all_text = '\n\n'.join(all_texts)
    return all_text


# ====================
def get_q_a_text(qa: bs4.element.Tag, year: int) -> str:
    """Get the text from a question or answer tag, provided it was written in
    the year specified"""

    # Return None if the posted date cannot be determined
    time = qa.find(name='time')
    if not time:
        return None

    # Return None if the year is not the required year or cannot be determined
    year_ = int(get_all_text(time).partition('/')[0])
    if not year_:
        return None
    if year_ != year:
        return None

    # Return text content, if found
    text_tag = qa.find(name=['div', 'p'], class_=['q_text', 'a_text'])
    if not text_tag:
        return None
    return get_all_text(text_tag)


# ====================
def print_test_page(url: str, year: int):
    """Print category and save text content to current working directory
    for a single page with the given URL."""

    page_result = PageResult(url, year)
    if page_result.success:
        print(page_result.success)
        print(page_result.category)
        save_text_to_file(page_result.text, './test.txt')
    else:
        print(page_result.err_msg)


# ====================
if __name__ == "__main__":

    print_test_page(TEST_PAGE_URL, TEST_PAGE_YEAR)
