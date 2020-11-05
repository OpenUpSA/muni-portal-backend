from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.core import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from muni_portal.core.api import api_router
from muni_portal.core.views import Index, WebhooksView

urlpatterns = [
    path("", Index.as_view(), name="index"),
    path("notifications", include("muni_portal.notifications.urls")),
    path("admin/", admin.site.urls),
    path("cms/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("api/webhooks/", WebhooksView.as_view(), name="webhooks"),
    path("api/wagtail/v2/", api_router.urls),
    path("", include(wagtail_urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
