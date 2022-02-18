from os import listdir, makedirs, remove
from os.path import isdir, isfile, join, dirname
import shutil


# ====================
def save_text_to_file(text: str, file_path: str):

    makedirs(dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(text)


# ====================
def get_text_from_file(file_path: str) -> str:

    with open(file_path, errors='ignore') as f:
        text = f.read()
    return text


# ====================
def get_file_paths(folder_path: str) -> list:

    return [join(folder_path, f)
            for f in listdir(folder_path)
            if isfile(join(folder_path, f))]


# ====================
def write_line_to_file(line: str, path: str):

    with open(path, 'a', encoding='utf-8') as f:
        f.write(f'{line}\n')


# ====================
def create_blank_if_not_exist(file_path: str):

    if not isfile(file_path):
        save_text_to_file("", file_path)


# ====================
def get_files_and_folders(path: str, full_path: bool = True) -> tuple:

    if full_path:
        files_and_folders = [join(path, e) for e in listdir(path)]
        files = [e for e in files_and_folders if isfile(e)]
        folders = [e for e in files_and_folders if isdir(e)]
    else:
        files_and_folders = [e for e in listdir(path)]
        files = [e for e in files_and_folders if isfile(join(path, e))]
        folders = [e for e in files_and_folders if isdir(join(path, e))]
    return (files, folders)

