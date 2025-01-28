from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from api.internal.app import ninja_api, ninja_admin_api
from . import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", ninja_api.urls),
    # path("api/admin/", ninja_admin_api.urls),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
