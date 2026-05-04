from django.urls import path

from . import views

app_name = "produtos"

urlpatterns = [
    path("categorias/", views.CategoriaListView.as_view(), name="categoria_list"),
    path("categorias/nova/", views.CategoriaCreateView.as_view(), name="categoria_create"),
    path("categorias/<int:pk>/editar/", views.CategoriaUpdateView.as_view(), name="categoria_update"),
    path("fornecedores/", views.FornecedorListView.as_view(), name="fornecedor_list"),
    path("fornecedores/novo/", views.FornecedorCreateView.as_view(), name="fornecedor_create"),
    path("fornecedores/<int:pk>/editar/", views.FornecedorUpdateView.as_view(), name="fornecedor_update"),
    path("tipos-fornecedor/", views.TipoFornecedorListView.as_view(), name="tipo_fornecedor_list"),
    path("tipos-fornecedor/novo/", views.TipoFornecedorCreateView.as_view(), name="tipo_fornecedor_create"),
    path("catalogo/", views.ProdutoListView.as_view(), name="produto_list"),
    path("catalogo/novo/", views.ProdutoCreateView.as_view(), name="produto_create"),
    path("catalogo/<int:pk>/editar/", views.ProdutoUpdateView.as_view(), name="produto_update"),
    path("lotes/", views.LoteListView.as_view(), name="lote_list"),
    path("lotes/novo/", views.LoteCreateView.as_view(), name="lote_create"),
]
