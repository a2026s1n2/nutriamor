from django import forms

from .models import Categoria, Fornecedor, Lote, Produto, TipoFornecedor


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ("nome", "descricao", "ativo")


class TipoFornecedorForm(forms.ModelForm):
    class Meta:
        model = TipoFornecedor
        fields = ("nome",)


class FornecedorForm(forms.ModelForm):
    class Meta:
        model = Fornecedor
        fields = (
            "tipo_fornecedor",
            "razao_social",
            "nome_fantasia",
            "documento",
            "telefone",
            "email",
            "cidade",
            "uf",
            "ativo",
        )


class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = (
            "categoria",
            "codigo",
            "descricao",
            "unidade_medida",
            "estoque_minimo",
            "controla_validade",
            "ativo",
        )


class LoteForm(forms.ModelForm):
    class Meta:
        model = Lote
        fields = ("produto", "fornecedor", "codigo_lote", "data_validade", "quantidade_atual")
