from typing import List, Dict

from ninja import NinjaAPI, Router

from api.internal.obscenity_filter.transport.handlers import TextHandler
from api.internal.obscenity_filter.transport.requests import TextIn
from api.internal.obscenity_filter.transport.responses import ObsceneWordsOut


def get_texts_router(text_handler: TextHandler):
    def f(request, text_in: TextIn):
        return text_handler.check_text(request, text_in)

    def k(request, text_in: TextIn):
        return text_handler.get_similar_words(request, text_in)

    router = Router(tags=["texts"])
    router.add_api_operation(
        "", ["POST"], f, response={200: str, 400: str}
    )
    router.add_api_operation(
        "obscene-words", ["POST"], k, response={200: Dict[str, List[ObsceneWordsOut]]}
    )

    return router


def add_texts_routers(api: NinjaAPI, text_handler: TextHandler):
    client_router = get_texts_router(text_handler)
    api.add_router("/text", client_router)
    return api
