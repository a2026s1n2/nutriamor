from django.contrib import admin

from .models import Danfe, DanfeItem, Inventario, InventarioItem, Movimentacao, TipoMovimentacao


@admin.register(TipoMovimentacao)
class TipoMovimentacaoAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nome")


class DanfeItemInline(admin.TabularInline):
    model = DanfeItem
    extra = 0


@admin.register(Danfe)
class DanfeAdmin(admin.ModelAdmin):
    list_display = ("numero", "serie", "fornecedor", "chave_44", "valor_total")
    inlines = [DanfeItemInline]


@admin.register(Movimentacao)
class MovimentacaoAdmin(admin.ModelAdmin):
    list_display = ("tipo_movimentacao", "lote", "quantidade", "usuario", "data_movimento", "criado_em")
    list_filter = ("tipo_movimentacao",)


class InventarioItemInline(admin.TabularInline):
    model = InventarioItem
    extra = 0


@admin.register(Inventario)
class InventarioAdmin(admin.ModelAdmin):
    list_display = ("data_inventario", "usuario")
    inlines = [InventarioItemInline]
