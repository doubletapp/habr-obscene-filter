from openai import OpenAI

from api.internal.obscenity_filter.services.obscenity_filter import ObscenityFilterService
from api.internal.obscenity_filter.transport.handlers import TextHandler
from config.settings import CHATGPT_API_KEY, SUSPICIOUS_WORDS_CHECK, CHATGPT_BASE_URL

if SUSPICIOUS_WORDS_CHECK:
    obscenity_filter_service = ObscenityFilterService(
        suspicious_words_check=SUSPICIOUS_WORDS_CHECK,
        gpt_client=OpenAI(
            api_key=CHATGPT_API_KEY,
            base_url=CHATGPT_BASE_URL,
        )
    )
else:
    obscenity_filter_service = ObscenityFilterService()
texts_handler = TextHandler(obscenity_filter_service)
