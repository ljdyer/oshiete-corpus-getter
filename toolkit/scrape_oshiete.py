"""
scrape_oshiete.py

Scrapes pages from the website oshiete.goo.ne.jp

Settings should be stored in JSON format in the location specified by
PROGRESS_JSON_PATH, with a key for each year (e.g. '2001') each containing
another object with keys 'continue_from' and 'end' specifying the page IDs
to continue from and end on.

Run the program by calling it from the terminal with the year specified as
an argument.

E.g.
> python scrape.oshiete.py 2001

The program can be terminated at any time by pressing Ctrl+C and will
save its progress by updating the value of 'continue_from' for the year
it was scraping for in the progress JSON.
"""

import argparse
import csv
import json
import os
from helper.file_helper import (
    create_blank_if_not_exist, save_text_to_file, write_line_to_file
)
from toolkit.get_oshiete_article import PageResult

CORPUS_PATH = "E:/oshiete_corpus/"
LOG_FILE_PATH = os.path.join(CORPUS_PATH, "log.csv")
PROGRESS_JSON_PATH = 'progress.json'


# ====================
def get_args():
    """Get command-line arguments"""

    parser = argparse.ArgumentParser(
        description='Scrape oshiete.goo.ne.jp',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('year',
                        metavar='year',
                        help='The year to scrape content from')
    return parser.parse_args()


# ====================
def load_progress() -> dict:

    with open(PROGRESS_JSON_PATH, 'r') as file:
        progress = json.load(file)
    return progress


# ====================
def save_progress(progress: dict):

    with open(PROGRESS_JSON_PATH, 'w') as file:
        json.dump(progress, file)


# ====================
def make_url(id: int) -> str:

    return f"https://oshiete.goo.ne.jp/qa/{id}.html"


# ====================
def read_log(log_path: str):

    with open(log_path, encoding='utf-8') as csv_file:
        files = []
        urls = []
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            files.append(row[0])
            urls.append(row[1])
    return (files, urls)


# ====================
def get_next_file_num(existing_files):

    existing_file_nums = [int(file_name.split('.')[0])
                          for file_name in existing_files]
    next_file_num = max(existing_file_nums, default=0) + 1
    return next_file_num


# ====================
def get_articles(year: int):

    create_blank_if_not_exist(LOG_FILE_PATH)
    existing_files, existing_urls = read_log(LOG_FILE_PATH)
    next_file_num = get_next_file_num(existing_files)

    progress = load_progress()
    start_id = progress[str(year)]["continue_from"]
    end_id = progress[str(year)]["end"]

    try:
        for id in range(start_id, end_id):

            url = make_url(id)
            if url in existing_urls:
                print(f"{url}\tAlready in corpus.")
                continue

            result = PageResult(url, year)
            if not result.success:
                print(f"{url}\t{result.err_msg}")
                continue

            # Save the new file to the corpus
            file_name = f"{next_file_num}.txt"
            file_path = os.path.join(
                CORPUS_PATH, str(year), result.category, file_name
            )
            save_text_to_file(result.text, file_path)
            next_file_num += 1
            # Update the log
            log = f"{file_name},{url},{result.category},{year}"
            write_line_to_file(log, LOG_FILE_PATH)
            print(f"{url}\t{file_name}")

    except KeyboardInterrupt:
        print(f"You terminated the program while processing id: {id}.")
        progress[str(year)]['continue_from'] = id
        save_progress(progress)
        print("Progress file has been updated")

    except Exception as e:
        print(f"The program terminated due to a <<<{e}>>> error",
              f"while processing id: {id}.")
        progress[str(year)]['continue_from'] = id
        save_progress(progress)
        print("Progress file has been updated")

    print()
    print("Finished.")


# ====================
def main():

    args = get_args()
    year = str(args.year)
    progress = load_progress()
    if year in progress:
        get_articles(year)
    else:
        print("No settings information available for that year.",
              "Please add settings information or choose from one of the",
              f"following years: {progress.keys()}")


# ====================
if __name__ == "__main__":

    main()
