from os import listdir
from os.path import dirname, isdir, isfile, join, normpath, relpath

from helper.text_helper import jp_word_count

CORPUS_PATH = "E:/oshiete_corpus/"
CORPUS_PARENT = dirname(normpath(CORPUS_PATH))


# ====================
class Folder:

    # ====================
    def __init__(self, path):

        path = normpath(path)
        self.abs_path = path
        rel_path = (relpath(path, CORPUS_PARENT))
        path_split = rel_path.split('\\')
        self.level = len(path_split) - 1
        self.base_name = path_split[-1]
        files, subfolders = get_files_and_folders(path)
        if not subfolders:
            self.num_files = len(files)
            self.total_word_count = sum_of_word_counts(files)
        self.subfolders = [Folder(sf) for sf in subfolders]

    # ====================
    def display(self):

        num_files = self.get_num_files()
        total_word_count = self.get_total_word_count()
        print(
            f"{chr(9) * self.level}{self.base_name}:",
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
def sum_of_word_counts(files: str):

    word_counts = [jp_word_count(fn) for fn in files]
    return(sum(word_counts))


# ====================
def get_files_and_folders(path: str) -> tuple:

    files_and_folders = [join(path, e) for e in listdir(path)]
    files = [e for e in files_and_folders if isfile(e)]
    folders = [e for e in files_and_folders if isdir(e)]
    return (files, folders)


corpus_folder = Folder(CORPUS_PATH)
corpus_folder.display()
