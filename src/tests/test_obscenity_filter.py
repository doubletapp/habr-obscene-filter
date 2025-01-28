import pytest

from api.internal.obscenity_filter.models import ObsceneWord
from api.internal.obscenity_filter.services.obscenity_filter import ObscenityFilterService


@pytest.fixture
def obscenity_filter_service(db):
    return ObscenityFilterService(obscenity_indicator=0.6)


@pytest.fixture
def fill_obscene_words(db, obscenity_filter_service):
    words = ["Банан", "Яблоко", "Груша", "Гранат"]
    for word in words:
        obscenity_filter_service.create_obscene_word(word)


def test_created_obscene_word_exists(fill_obscene_words):
    assert ObsceneWord.objects.all().count() == 4


@pytest.mark.parametrize(
    "new_word",
    ["Пиво", "Пиво с рыбкой", " Агент007 "],
)
def test_created_interest_exists(fill_obscene_words, obscenity_filter_service, new_word):
    new_obscene_word = obscenity_filter_service.create_obscene_word(new_word)
    assert new_obscene_word.value == new_word
    ObsceneWord.objects.get(value=new_obscene_word.value)


@pytest.mark.parametrize(
    "new_word, new_normalized_word",
    [
        ("Пиво", "pivo"),
        ("Пиво с рыбкой", "pivosrybkoj"),
        (" Агент007 ", "agent007"),
    ],
)
def test_normalize_word(fill_obscene_words, obscenity_filter_service, new_word, new_normalized_word):
    new_obscene_word = obscenity_filter_service.create_obscene_word(new_word)
    assert new_obscene_word.normalized_value == new_normalized_word
    ObsceneWord.objects.get(value=new_obscene_word.value)


@pytest.mark.parametrize(
    "word, collapsed_word",
    [
        ("ППиииввввооо", "Пиво"),
        ("П11111во", "П1во"),
        ("000000001111111", "01"),
    ],
)
def test_collapse_word(obscenity_filter_service, word, collapsed_word):
    assert collapsed_word == obscenity_filter_service.collapse_repeating_characters(word)


@pytest.mark.parametrize(
    "word, numbers_translated_word",
    [("П1во", "Пиво"), ("Пр0гулять", "Прогулять"), ("0123456789", "ои2зчsбгВ9")],
)
def test_numbers_translate(obscenity_filter_service, word, numbers_translated_word):
    assert numbers_translated_word == obscenity_filter_service.replace_numbers_to_letters(word)


@pytest.mark.parametrize(
    "word, transformed_word",
    [("ypoк", "урок"), ("Taпoк", "Тапок")],
)
def test_replace_similar_latin_to_cyrillic(obscenity_filter_service, word, transformed_word):
    assert transformed_word == obscenity_filter_service.replace_similar_latin_to_cyrillic(word)


@pytest.mark.parametrize(
    "word, is_word_obscene",
    [
        ("Банан", True),
        ("Груша", True),
        ("Банан0", True),
        ("бУнан", False),
        ("БАНАН", True),
        ("Бананы", True),
        ("Бaнaн", True),  # english a
        ("Ябл0ки", True),
        ("Барбарики", False),
        ("Помидор", False),
        ("Грушевидный", False),
    ],
)
def test_is_word_obscene(fill_obscene_words, obscenity_filter_service, word, is_word_obscene):
    assert is_word_obscene == obscenity_filter_service.is_word_obscene(word)


@pytest.mark.parametrize(
    "text, is_text_obscene",
    [
        ("Бананы очень вкусные", True),
        ("Помидоры очень вкусные", False),
    ],
)
def test_is_text_obscene(fill_obscene_words, obscenity_filter_service, text, is_text_obscene):
    assert is_text_obscene == obscenity_filter_service.is_text_obscene(text)
