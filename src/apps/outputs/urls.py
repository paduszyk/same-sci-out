from django.urls import include, path

urlpatterns = [
    path("contributions/", include("apps.outputs.contributions.urls")),
    path("elements/", include("apps.outputs.elements.urls")),
]
