from os import listdir, makedirs
from os.path import isfile, join, dirname


# ====================
def save_text_to_file(text: str, file_path: str):

    makedirs(dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(text)


# ====================
def get_num_chars(file_path: str) -> int:

    with open(file_path, errors='ignore') as f:
        text = f.read()
    return len(text)


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
