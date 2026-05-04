from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView

from apps.core.mixins import EscritaNecessariaMixin

from .forms import CategoriaForm, FornecedorForm, LoteForm, ProdutoForm, TipoFornecedorForm
from .models import Categoria, Fornecedor, Lote, Produto, TipoFornecedor


class CategoriaListView(ListView):
    model = Categoria
    template_name = "produtos/categoria_list.html"
    context_object_name = "itens"


class CategoriaCreateView(EscritaNecessariaMixin, CreateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = "produtos/form_generico.html"
    success_url = reverse_lazy("produtos:categoria_list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["titulo"] = "Nova categoria"
        return ctx


class CategoriaUpdateView(EscritaNecessariaMixin, UpdateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = "produtos/form_generico.html"
    success_url = reverse_lazy("produtos:categoria_list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["titulo"] = "Editar categoria"
        return ctx


class TipoFornecedorListView(ListView):
    model = TipoFornecedor
    template_name = "produtos/tipo_fornecedor_list.html"
    context_object_name = "itens"


class TipoFornecedorCreateView(EscritaNecessariaMixin, CreateView):
    model = TipoFornecedor
    form_class = TipoFornecedorForm
    template_name = "produtos/form_generico.html"
    success_url = reverse_lazy("produtos:tipo_fornecedor_list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["titulo"] = "Novo tipo de fornecedor"
        return ctx


class FornecedorListView(ListView):
    model = Fornecedor
    template_name = "produtos/fornecedor_list.html"
    context_object_name = "itens"


class FornecedorCreateView(EscritaNecessariaMixin, CreateView):
    model = Fornecedor
    form_class = FornecedorForm
    template_name = "produtos/form_generico.html"
    success_url = reverse_lazy("produtos:fornecedor_list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["titulo"] = "Novo fornecedor / doador"
        return ctx


class FornecedorUpdateView(EscritaNecessariaMixin, UpdateView):
    model = Fornecedor
    form_class = FornecedorForm
    template_name = "produtos/form_generico.html"
    success_url = reverse_lazy("produtos:fornecedor_list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["titulo"] = "Editar fornecedor"
        return ctx


class ProdutoListView(ListView):
    model = Produto
    template_name = "produtos/produto_list.html"
    context_object_name = "itens"


class ProdutoCreateView(EscritaNecessariaMixin, CreateView):
    model = Produto
    form_class = ProdutoForm
    template_name = "produtos/form_generico.html"
    success_url = reverse_lazy("produtos:produto_list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["titulo"] = "Novo produto"
        return ctx


class ProdutoUpdateView(EscritaNecessariaMixin, UpdateView):
    model = Produto
    form_class = ProdutoForm
    template_name = "produtos/form_generico.html"
    success_url = reverse_lazy("produtos:produto_list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["titulo"] = "Editar produto"
        return ctx


class LoteListView(ListView):
    model = Lote
    template_name = "produtos/lote_list.html"
    context_object_name = "itens"
    paginate_by = 25


class LoteCreateView(EscritaNecessariaMixin, CreateView):
    model = Lote
    form_class = LoteForm
    template_name = "produtos/form_generico.html"
    success_url = reverse_lazy("produtos:lote_list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["titulo"] = "Novo lote"
        ctx["ajuda"] = (
            "Para entrada sem nota, cadastre o lote e depois registre uma movimentação "
            "do tipo ENTRADA em Estoque."
        )
        return ctx
