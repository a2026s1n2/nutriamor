from django.contrib import admin

from .models import Categoria, Fornecedor, Lote, Produto, TipoFornecedor


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nome", "ativo")
    list_filter = ("ativo",)


@admin.register(TipoFornecedor)
class TipoFornecedorAdmin(admin.ModelAdmin):
    list_display = ("nome",)


@admin.register(Fornecedor)
class FornecedorAdmin(admin.ModelAdmin):
    list_display = ("razao_social", "documento", "tipo_fornecedor", "ativo")
    list_filter = ("ativo", "tipo_fornecedor")


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ("codigo", "descricao", "categoria", "estoque_minimo", "ativo")
    list_filter = ("ativo", "categoria")


@admin.register(Lote)
class LoteAdmin(admin.ModelAdmin):
    list_display = ("codigo_lote", "produto", "fornecedor", "quantidade_atual", "data_validade")
    list_filter = ("produto", "fornecedor")
