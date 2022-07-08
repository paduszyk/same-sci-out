from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("units/", include("apps.units.urls")),
    path("employees/", include("apps.employees.urls")),
    path("outputs/", include("apps.outputs.urls")),
    path("extras/", include("apps.extras.urls")),
    path("__debug__/", include("debug_toolbar.urls")),
]

urlpatterns = (
    urlpatterns
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
)
