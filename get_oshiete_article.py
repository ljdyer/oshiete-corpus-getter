from helper.file_helper import save_text_to_file
from helper.html_helper import get_bs, get_all_text
import bs4

TEST_PAGE = "https://oshiete.goo.ne.jp/qa/193972.html"


class PageResult:

    def __init__(self, url: str, year: int):

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
            self.err_msg = f'<<<{e}>>> error while attempting to determine category.'
            return

        # Get text content from questions and answers
        try:
            self.text = get_all_q_and_a_text(bs, year)
        except Exception as e:
            self.success = False
            self.err_msg = f"<<<{e}>>> error while parsing!"
            return

        # Make sure there is some content to return
        if self.text.isspace():
            self.success = False
            self.err_msg = f"Did not find any content written in {year}."
            return
        else:
            self.success = True
            return


# ====================
def get_main_category(bs: bs4.BeautifulSoup) -> str:

    all_categories = bs.find(id='crumb')
    main_category = all_categories.findAll(name='a')[1].text
    return main_category


# ====================
def get_all_q_and_a_text(bs: bs4.BeautifulSoup, year: int) -> str:

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
if __name__ == "__main__":

    page_result = PageResult(TEST_PAGE, 2002)
    if page_result.success:
        print(page_result.category)
        save_text_to_file(page_result.text, 'test/test.txt')
    else:
        print(page_result.err_msg)
