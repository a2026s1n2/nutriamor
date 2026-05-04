from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include(("apps.core.urls", "core"), namespace="core")),
    path("produtos/", include(("apps.produtos.urls", "produtos"), namespace="produtos")),
    path("estoque/", include(("apps.estoque.urls", "estoque"), namespace="estoque")),
]
