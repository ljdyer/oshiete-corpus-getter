"""
corpus_compiler.py

Build a diachronic corpus of Japanese from a collection of individual
documents saved as .txt files.

The folder specified in CORPUS_PATH should have the following format:

CORPUS_PATH
├── year1
│     ├── category1
│     ├── category2
│     ├── category3
│     ├── etc.
├── year2
│     ├── category1
│     ├── category2
│     ├── category4
│     ├── etc.
└── etc.

Where the category folders contain .txt files containing Japanese text.

Only categories present in both years will be included in the corpus.
Documents will be chosen such that the number of words in each year is
roughly equal for each category.

Non-tokenized ('raw') and tokenized versions of the corpus will be saved.
Non-tokenized files will be saved in 'CORPUS_PATH/raw' and tokenized
files will be saved in 'CORPUS_PATH/tokenized'.
"""

from os.path import join as joinpath

import pandas as pd

from helper.file_helper import get_files_and_folders
from helper.text_helper import (jp_word_count, sum_of_jp_word_counts,
                                word_tokenize_line)
from helper.file_helper import save_text_to_file

CORPUS_PATH = "E:/oshiete_corpus/"
YEARS = ['2001', '2021']
EXCLUDE_CATEGORIES = ['gooサービス', '公式アカウントからの質問']
CATEGORY_NAME_TRANSLATIONS = {
    "ビジネス・キャリア": 'business-career',
    "悩み相談・人生相談": 'life-advice',
    "エンターテインメント・スポーツ": 'entertainment-sports',
    "ニュース・災害・社会制度": 'news-disasters-social-structure',
    "趣味・アウトドア・車": 'hobbies-outdoors-cars',
    "インターネット・Webサービス": 'entertainment-web-services',
    "地域情報・旅行・お出かけ": 'local-info-travel-going-out',
    "お金・保険・資産運用": 'money-insurance-wealth-management',
    "パソコン・スマホ・電化製品": 'computers-smartphones-electronics',
    "暮らし・生活・行事": 'lifestyle-events',
    "教育・科学・学問": 'education-science-learning',
    "健康・美容・ファッション": 'health-beauty-fashion',
    "コンピューター・テクノロジー": 'computing-technology'
}
ARTICLE_END_TAG = "</article>"


# ====================
def build_corpus():
    """Build the corpus.

    See the module documentation for details."""

    # Get categories to include
    categories = get_common_categories(exclude=EXCLUDE_CATEGORIES)
    print("Including the following categories",
          ", ".join(categories))
    print()

    # Get word counts for each category
    print('Word counts for each category in each year:')
    category_counts = get_category_counts(categories)
    print()

    # Build the corpus and get information about the files created
    print('Building corpus...')
    files_and_word_counts = get_files_and_word_counts(category_counts)
    generate_corpus_files(files_and_word_counts)
    print()

    wc_info = get_category_word_count_info(files_and_word_counts)
    wc_info_df = pd.DataFrame(wc_info)
    wc_info_df = wc_info_df.transpose()
    wc_info_df = wc_info_df.append(
        wc_info_df.sum(numeric_only=True).rename('Total'))
    excel_path = joinpath(CORPUS_PATH, 'word_counts.xlsx')
    wc_info_df.to_excel(excel_path)
    print(f'Word count info saved to {excel_path}.')


# ====================
def year_path(category: str):

    return joinpath(CORPUS_PATH, category)


# ====================
def category_path(year: str, category: str):

    return joinpath(CORPUS_PATH, year, category)


# ====================
def get_common_categories(exclude=[]):
    """Get the list of categories that are present for both years and are not
    in the list of excluded categories"""

    year_categories = []
    for year in YEARS:
        _, folders = get_files_and_folders(year_path(year),
                                           full_path=False)
        year_categories.append(folders)
    common_categories = set.intersection(*map(set, year_categories))
    common_categories = [c for c in common_categories if c not in exclude]
    return common_categories


# ====================
def get_category_counts(categories: list) -> dict:
    """Count how many total words are available for each category for each
    year"""

    category_counts = {category: {} for category in categories}
    for category in category_counts.keys():
        word_count_info = f"{category}: "
        for year in YEARS:
            files, _ = get_files_and_folders(category_path(year, category))
            year_words = sum_of_jp_word_counts(files)
            category_counts[category][year] = year_words
            word_count_info = word_count_info + f'{year}: {year_words}; '
        print(word_count_info)
    return category_counts


# ====================
def files_to_reach_target(available_files: list,
                          target_word_count: int) -> tuple:
    """Select a subset of the list of available files to reach the target
    word count

    Return a tuple (files, word_count) with the files to use and the total
    number of words in the files"""

    files_to_use = []
    words_so_far = 0
    # Add files to the list of files to use until the total word count exceeds
    # the target
    for file in available_files:
        files_to_use.append(file)
        words_so_far += jp_word_count(file)
        if words_so_far >= target_word_count:
            return (files_to_use, words_so_far)
    else:
        raise ValueError(f'Not enough words. Target is {target_word_count} '
                         f'words, but only {words_so_far} were found in the ' +
                         'list of files provided.')


# ====================
def get_files_and_word_counts(category_counts: dict) -> dict:
    """Generate lists of files for each category for each year such that there
    will be a roughly equal number of words in each category for each year"""

    files_and_word_counts = {category: {}
                             for category in category_counts.keys()}
    for category in category_counts.keys():
        target_word_count = min([category_counts[category][year]
                                 for year in YEARS])
        for year in YEARS:
            path = (joinpath(CORPUS_PATH, year, category))
            all_files, _ = get_files_and_folders(path)
            # If this is the year with the fewest words available, include all
            # the files
            if category_counts[category][year] == target_word_count:
                files_and_word_counts[category][year] \
                    = (all_files, target_word_count)
            # Otherwise, stop adding files at the point where the target word
            # count is reached
            else:
                files_and_word_counts[category][year] = \
                    files_to_reach_target(all_files, target_word_count)

    return files_and_word_counts


# ====================
def generate_corpus_files(files_and_word_counts: dict):

    file_info = {}

    for category in files_and_word_counts.keys():
        for year in YEARS:
            # Generate paths for .txt files to save to.
            # Translate category names to English because AntConc cannot handle
            # non-ASCII file names.
            target_fn = f'{year}_{CATEGORY_NAME_TRANSLATIONS[category]}.txt'
            target_path_raw = joinpath(CORPUS_PATH, 'raw', target_fn)
            target_path_tokenized = joinpath(CORPUS_PATH, 'tokenized',
                                             target_fn)
            # Generate concatenated text files
            source_files, word_count = files_and_word_counts[category][year]
            concatenate_text_files(source_files, target_path_raw,
                                   target_path_tokenized)
            print(f'{target_fn}: {word_count} words')
            file_info[target_fn] = word_count

    return file_info
    

# ====================
def get_category_word_count_info(files_and_word_counts: dict):

    wc_info = {category: {}
               for category in files_and_word_counts.keys()}
    # Get EN translation of category name
    for category in wc_info.keys():
        wc_info[category]['EN'] = CATEGORY_NAME_TRANSLATIONS[category]
        # Get word counts for each year
        for year in files_and_word_counts[category].keys():
            wc_info[category][year] = \
                files_and_word_counts[category][year][1]
    return wc_info


# ====================
def concatenate_text_files(source_files: list, target_path_raw: str,
                           target_path_tokenized: str):

    save_text_to_file('', target_path_raw)
    with open(target_path_raw, 'w', encoding='utf-8') as target_file:
        for f in source_files:
            with open(f, 'r', encoding='utf-8') as source_file:
                target_file.write(article_start_tag(f))
                target_file.write('\n')
                for line in source_file.readlines():
                    target_file.write(line)
                target_file.write(ARTICLE_END_TAG)
                target_file.write('\n\n')

    save_text_to_file('', target_path_tokenized)
    with open(target_path_tokenized, 'w', encoding='utf-8') as target_file:
        for f in source_files:
            with open(f, 'r', encoding='utf-8') as source_file:
                target_file.write(article_start_tag(f))
                target_file.write('\n')
                for line in source_file.readlines():
                    target_file.write(word_tokenize_line(line))
                target_file.write(ARTICLE_END_TAG)
                target_file.write('\n\n')


# ====================
def article_start_tag(source_file_path: str):

    return f'<article localpath="{source_file_path}">'


# ====================
if __name__ == "__main__":

    build_corpus()
