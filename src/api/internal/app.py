from ninja import NinjaAPI

from api.internal.obscenity_filter.app import texts_handler
from api.internal.obscenity_filter.routers import add_texts_routers
from config import settings


def get_api():
    api = NinjaAPI(title="Obscene filter api", auth=None, version=settings.API_VERSION)
    # admin_api = NinjaAPI(
    #     title="DTIS admin api", docs_url="docs", auth=[HTTPJWTAuth()], version=settings.ADMIN_API_VERSION
    # )
    admin_api = None

    add_texts_routers(api, texts_handler)

    return api, admin_api


ninja_api, ninja_admin_api = get_api()
