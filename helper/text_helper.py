import fugashi

tagger = fugashi.Tagger()


# ====================
def jp_word_count(file_path: str) -> tuple:

    with open(file_path, encoding='utf-8') as f:
        text = f.read()
        word_count = len(tagger(text))

    return word_count
