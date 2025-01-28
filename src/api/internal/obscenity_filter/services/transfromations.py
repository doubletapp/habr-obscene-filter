import re


def collapse_repeating_characters(input_string: str) -> str:
    """
    Collapses consecutive repeating characters into a single instance.
    """
    return re.sub(r"(.)\1+", r"\1", input_string)


def replace_numbers_to_letters(word: str) -> str:
    """
    Replaces numeric characters with visually similar letters.
    """
    numbers_to_letters = {"0": "о", "1": "и", "3": "з", "4": "ч", "5": "s", "6": "б", "7": "г", "8": "В"}
    return word.translate(str.maketrans(numbers_to_letters))


def replace_similar_latin_to_cyrillic(word: str) -> str:
    """
    Replaces latin characters with visually similar letters in cyrillic.
    """
    numbers_to_letters = {
        "y": "у",
        "e": "е",
        "o": "о",
        "p": "р",
        "a": "а",
        "k": "к",
        "x": "х",
        "c": "с",
        "E": "E",
        "T": "Т",
        "O": "О",
        "P": "Р",
        "А": "А",
        "H": "Н",
        "K": "К",
        "X": "Х",
        "C": "C",
        "B": "В",
        "M": "М",
        "n": "п",
    }
    return word.translate(str.maketrans(numbers_to_letters))


DEFAULT_TRANSFORMATIONS = [
    lambda x: x,
    replace_numbers_to_letters,
    collapse_repeating_characters,
    replace_similar_latin_to_cyrillic,
]
