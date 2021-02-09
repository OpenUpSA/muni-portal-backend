from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.core import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from muni_portal.core.api import api_router
from muni_portal.core.views import (
    IndexView,
    CollaboratorWebhookApiView,
)

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("notifications", include("muni_portal.notifications.urls")),
    path("admin/", admin.site.urls),
    path("cms/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path(
        "api/webhooks/collaborator/",
        CollaboratorWebhookApiView.as_view(),
        name="webhooks",
    ),
    path("api/accounts/", include("rest_registration.api.urls")),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/wagtail/v2/", api_router.urls),
    path("", include(wagtail_urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
