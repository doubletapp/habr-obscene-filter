from typing import List, Dict

from api.internal.obscenity_filter.services.obscenity_filter import ObscenityFilterService
from api.internal.obscenity_filter.transport.requests import TextIn
from api.internal.obscenity_filter.transport.responses import ObsceneWordsOut


class TextHandler:
    def __init__(self, obscenity_filter_service: ObscenityFilterService):
        self._obscenity_filter_service = obscenity_filter_service

    def check_text(self, request, text_in: TextIn) -> (int, str):
        text = text_in.text
        if self._obscenity_filter_service.is_text_obscene(text):
            return 400, "Obscene word!"
        return 200, "Your text is fine!"

    def get_similar_words(self, request, text_in: TextIn) -> (int, Dict[str, List[ObsceneWordsOut]]):
        text = text_in.text
        words = self._obscenity_filter_service.get_similar_words(text)
        return 200, words
