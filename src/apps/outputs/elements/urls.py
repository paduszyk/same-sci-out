from django.urls import include, path

urlpatterns = [
    path("articles/", include("apps.outputs.elements.articles.urls")),
    path("patents/", include("apps.outputs.elements.patents.urls")),
    path("projects/", include("apps.outputs.elements.projects.urls")),
]
