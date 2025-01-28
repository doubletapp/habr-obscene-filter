import re

from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import F, Q

from api.internal.obscenity_filter.models import ObsceneWord, SuspiciousWord
from api.internal.obscenity_filter.services.transfromations import DEFAULT_TRANSFORMATIONS
from config.settings import OBSCENITY_INDICATOR


class ObscenityFilterService:
    """
    A service for filtering and detecting obscene words and phrases in text.

    This service provides functionality to:
    - Normalize words by removing unnecessary characters, converting to lowercase,
      and transliterating from Cyrillic to Latin.
    - Detect whether a word or text contains obscene language using trigram similarity.
    - Create and store obscene words in the database.

    Process of defining an obscene word:
    1. Transform word to other words based on assumptions, how characters or group of symbols might appear similar to symbols used in obscene word.
       For example: app1e is similar to apple, ccaatt is similar to cat
       !!! You can add more transformations to make filter more robust.
    2. Normalize initial and transformed words
       For example: " ЯблОkо" -> "yabloko"
    3. Find most similar words by trigrams and check if similarity is more than obscenity_indicator
    """

    TRANSLATION_DICT = {
        "а": "a",
        "б": "b",
        "в": "v",
        "г": "g",
        "д": "d",
        "е": "e",
        "ж": "zh",
        "з": "z",
        "и": "i",
        "й": "j",
        "к": "k",
        "л": "l",
        "м": "m",
        "н": "n",
        "о": "o",
        "п": "p",
        "р": "r",
        "с": "s",
        "т": "t",
        "у": "u",
        "ф": "f",
        "х": "kh",
        "ц": "c",
        "ч": "ch",
        "ш": "sh",
        "щ": "shch",
        "ъ": "",
        "ы": "y",
        "ь": "",
        "э": "e",
        "ю": "yu",
        "я": "ya",
        "ё": "e",
    }


    def __init__(
            self,
            *,
            obscenity_indicator=OBSCENITY_INDICATOR,
            transformations=DEFAULT_TRANSFORMATIONS,
            suspicious_words_check=False,
            gpt_client=None,
    ):
        self.obscenity_indicator = obscenity_indicator
        self.transformations = transformations
        self.suspicious_words_check = suspicious_words_check
        if self.suspicious_words_check and not gpt_client:
            raise ValueError("gpt_client must be defined too if suspicious_words_check is True")
        self.gpt_client = gpt_client

    def normalize_word(self, word: str) -> str:
        """
        Normalizes a word by performing the following operations:
        - Removes all non-alphanumeric characters (except Cyrillic).
        - Converts to lowercase.
        - Trims leading and trailing whitespace.
        - Transliterates Cyrillic letters to Latin equivalents.
        """
        filtered_word = re.sub(r"[^\w\dа-яА-ЯёЁ]", "", word, flags=re.UNICODE)
        lowered_word = filtered_word.lower()
        stripped_word = lowered_word.strip()
        translated_word = stripped_word.translate(str.maketrans(self.TRANSLATION_DICT))
        return translated_word

    def normalize_text(self, text: str) -> str:
        return " ".join(map(self.normalize_word, text.split(" ")))

    def _add_suspicious_words(self, text: str):
        # TODO: add async here
        completion = self.gpt_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": "Find words in the text that may be obscene"
                                            "Print ONLY found words separated by spaces without explanations"},
                {"role": "user", "content": text},
            ],
            temperature=0,
            top_p=1,
        )
        suspicious_words = completion.choices[0].message.content
        SuspiciousWord.objects.bulk_create(
            [SuspiciousWord(value=word) for word in suspicious_words.split(' ')],
            ignore_conflicts=True,
        )

    def _similarity_obscene_check(self, similarity: TrigramSimilarity) -> bool:
        similar_words = ObsceneWord.objects.annotate(
            calc_similarity=similarity
        ).filter(
            Q(calc_similarity__gt=self.obscenity_indicator)
            & (Q(similarity__isnull=True) | Q(calc_similarity__gt=F("similarity")))
        )
        return similar_words.count() > 0

    def get_similar_words(self, text, limit=1):
        similar_words_dict = dict()
        for word in text.split(" "):
            similar_words = ObsceneWord.objects.annotate(
                calc_similarity=TrigramSimilarity("normalized_value", self.normalize_word(word))
            ).order_by('-calc_similarity')[0:limit]
            similar_words_dict[word] = similar_words
        return similar_words_dict

    def is_word_obscene(self, word: str) -> bool:
        for transformation in self.transformations:
            normalized_word = self.normalize_word(transformation(word))
            if self._similarity_obscene_check(TrigramSimilarity("normalized_value", normalized_word)):
                return True
        return False

    def is_text_obscene(self, text: str) -> bool:
        """
        Determines if any word in a given text is obscene.
        """
        for word in text.split(" "):
            if self.is_word_obscene(word):
                return True

        if self.suspicious_words_check:
            self._add_suspicious_words(text)

        return False

    def create_obscene_word(self, word: str) -> ObsceneWord:
        """
        Creates or updates an obscene word in the database.
        """
        obscene_word, _ = ObsceneWord.objects.get_or_create(value=word)
        obscene_word.normalized_value = self.normalize_word(word)
        obscene_word.save()
        return obscene_word
