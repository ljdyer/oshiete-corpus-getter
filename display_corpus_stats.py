"""
display_corpus_stats.py

Prints a representation of the internal folder structure with fil and words
counts for each folder. Word counts for folders with files are the sum
of the words in the files in the folder. Word/file counts for folders with
subfolders are the sum of the word/file counts of their subfolders.

Works using recursion in the get_num_files and get_total_word_count methods
of the Folder class.

Should work for any folder structure, but it is assumed that files are only in
the base level, so any files in folders with subfolders are ignored.

Assumes that the only .txt files are in the folder, so behaviour may be
unpredictable if other types of files are included.
"""

import os
from os.path import basename, normpath, relpath

from helper.file_helper import get_files_and_folders
from helper.text_helper import sum_of_jp_word_counts

CORPUS_PATH = "E:/oshiete_corpus/"


# ====================
class Folder:

    # ====================
    def __init__(self, path):

        path = normpath(path)
        self.abs_path = path
        self.base_name = basename(path)
        if path == normpath(CORPUS_PATH):
            self.depth = 0
        else:
            self.depth = len(relpath(path, CORPUS_PATH).split('\\'))
        files, subfolders = get_files_and_folders(path)
        if not subfolders:
            self.num_files = len(files)
            self.total_word_count = sum_of_jp_word_counts(files)
        self.subfolders = [Folder(sf) for sf in subfolders]

    # ====================
    def display(self):

        num_files = self.get_num_files()
        total_word_count = self.get_total_word_count()
        print(
            f"{chr(9) * self.depth}{self.base_name}:",
            f"{num_files} files, {total_word_count} words"
        )
        for sf in self.subfolders:
            sf.display()

    # ====================
    def get_num_files(self):

        if hasattr(self, 'num_files'):
            return self.num_files
        else:
            return sum([sf.get_num_files() for sf in self.subfolders])

    # ====================
    def get_total_word_count(self):

        if hasattr(self, 'total_word_count'):
            return self.total_word_count
        else:
            return sum([sf.get_total_word_count() for sf in self.subfolders])


# ====================
def main():

    print('Getting file and word counts...')
    corpus_folder = Folder(CORPUS_PATH)
    os.system('cls')
    print()
    corpus_folder.display()
    print()


# ====================
if __name__ == "__main__":

    main()
