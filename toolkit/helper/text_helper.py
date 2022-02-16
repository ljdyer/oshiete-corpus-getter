import fugashi
from os import remove

tagger = fugashi.Tagger()


# ====================
def jp_word_count(file_path: str) -> tuple:

    with open(file_path, encoding='utf-8') as f:
        text = f.read()
        word_count = len(tagger(text))
    if len(text) == 0:
        raise RuntimeError(f'Empty file encountered: {file_path}\n'
                           "Terminating program.")
    return word_count



# ====================
def sum_of_jp_word_counts(files: str):

    word_counts = [jp_word_count(fn) for fn in files]
    return(sum(word_counts))


# ====================
def word_tokenize_line(jp_text: str):

    tokenized = ' '.join([word.surface for word in tagger(jp_text)])
    return tokenized

# ====================
def word_tokenize_file(input_path: str, output_path: str):

    with open(input_path, encoding='utf-8') as in_file, \
         open(output_path, "a", encoding='utf-8') as out_file:
        for line in in_file:
            out_file.write("\n" + word_tokenize_line(line))
