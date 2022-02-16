"""
corpus_compiler.py

#TODO Add documentation!
"""

from os.path import join as joinpath

import pandas as pd

from helper.file_helper import concatenate_text_files, get_files_and_folders
from helper.text_helper import jp_word_count, sum_of_jp_word_counts, word_tokenize_file

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


# ====================
def get_common_categories(exclude=[]):
    """Get the list of categories that are present for both years and are not
    in the list of excluded categories"""

    year_categories = []
    for year in YEARS:
        year_categories.append(get_files_and_folders(
            joinpath(CORPUS_PATH, year), full_path=False
        )[1])
    common_categories = set.intersection(*map(set, year_categories))
    common_categories = [c for c in common_categories if c not in exclude]
    return common_categories


# ====================
def get_category_counts(categories: list) -> dict:
    """Count how many total words are available for each category for each
    year"""

    category_counts = {category: {} for category in categories}
    for category in category_counts.keys():
        for year in YEARS:
            files, _ = get_files_and_folders(
                joinpath(CORPUS_PATH, year, category)
            )
            category_counts[category][year] = sum_of_jp_word_counts(files)
    return category_counts


# ====================
def files_to_reach_target(available_files: list, target_word_count: int):
    """Select a subset of files from a list of available files to reach the target
    word count"""

    files_to_use = []
    words_so_far = 0
    for file in available_files:
        files_to_use.append(file)
        words_so_far += jp_word_count(file)
        if words_so_far >= target_word_count:
            return files_to_use
    else:
        raise ValueError(f'Not enough words. Target is {target_word_count} '
                         f'words, but only {words_so_far} were found in the ' +
                         'list of files provided.')


# ====================
def get_file_lists(category_counts: dict) -> dict:
    """Generate lists of files for each category for each year such that there
    will be a roughly equal number of words for each category for each year"""

    files = {category: {} for category in category_counts.keys()}
    for category in category_counts.keys():
        target_word_count = min([category_counts[category][year]
                                 for year in YEARS])
        for year in YEARS:
            path = (joinpath(CORPUS_PATH, year, category))
            all_files, _ = get_files_and_folders(path)
            # If this is the year with the fewest words available, include all
            # the files
            if category_counts[category][year] == target_word_count:
                files[category][year] = all_files
            # Otherwise, stop adding files at the point where the target word
            # count is reached
            else:
                files[category][year] = files_to_reach_target(
                    all_files, target_word_count
                )

    return files


# ====================
def generate_corpus_files(file_lists):

    file_info = {category: {'EN': CATEGORY_NAME_TRANSLATIONS[category]}
                 for category in file_lists.keys()}
    for category in file_lists.keys():
        for year in YEARS:
            target_fn_raw = f'{year}_{CATEGORY_NAME_TRANSLATIONS[category]}.txt'
            target_fn_tokenized = f'{year}_{CATEGORY_NAME_TRANSLATIONS[category]}_tokenized.txt'
            target_path_raw = joinpath(CORPUS_PATH, target_fn_raw)
            target_path_tokenized = joinpath(CORPUS_PATH, target_fn_tokenized)
            concatenate_text_files(file_lists[category][year], target_path_raw)
            word_count = jp_word_count(target_path_raw)
            word_tokenize_file(target_path_raw, target_path_tokenized)
            print(f'{target_fn_raw}: {word_count} words')
            file_info[category][year] = word_count

    return file_info


# ====================
if __name__ == "__main__":

    categories = get_common_categories(exclude=EXCLUDE_CATEGORIES)
    print("The following categories are present for both years:",
          ", ".join(categories))
    print()

    category_counts = get_category_counts(categories)
    print('Word counts for each category in each year:')
    for category in category_counts.keys():
        word_count_info = "; ".join(
            [f"{year}: {words}"
             for year, words in category_counts[category].items()]
        )
        print(f'{category}: {word_count_info}')
    print()

    file_lists = get_file_lists(category_counts)
    print('Generating corpus files...')
    file_info = generate_corpus_files(file_lists)
    print()

    file_info_df = pd.DataFrame(file_info)
    file_info_df = file_info_df.transpose()
    file_info_df = file_info_df.append(
        file_info_df.sum(numeric_only=True).rename('Total'))
    excel_path = joinpath(CORPUS_PATH, 'word_counts.xlsx')
    file_info_df.to_excel(excel_path)
    print(f'Word count info saved to {excel_path}.')
