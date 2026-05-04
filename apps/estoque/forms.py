from django import forms
from django.utils import timezone

from apps.produtos.models import Fornecedor, Lote, Produto

from .models import Danfe, Movimentacao, TipoMovimentacao


class MovimentacaoForm(forms.ModelForm):
    class Meta:
        model = Movimentacao
        fields = ("lote", "tipo_movimentacao", "quantidade", "data_movimento", "observacao")
        widgets = {
            "data_movimento": forms.DateInput(attrs={"type": "date"}),
            "observacao": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        self.usuario = kwargs.pop("usuario")
        super().__init__(*args, **kwargs)
        if "data_movimento" in self.fields and not self.initial.get("data_movimento"):
            self.initial["data_movimento"] = timezone.localdate()

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.usuario = self.usuario
        if commit:
            obj.save()
        return obj


class MovimentacaoEntradaRapidaForm(forms.Form):
    """Fluxo doação/sem NFe: cria lote com quantidade inicial e movimentação ENTRADA (saldo atualizado pelo signal)."""

    produto = forms.ModelChoiceField(queryset=Produto.objects.filter(ativo=True))
    fornecedor = forms.ModelChoiceField(queryset=Fornecedor.objects.filter(ativo=True))
    codigo_lote = forms.CharField(max_length=80)
    data_validade = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))
    quantidade = forms.DecimalField(max_digits=14, decimal_places=3, min_value=0.001)
    observacao = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 2}))

    def save_movimentacao(self, usuario):
        from apps.produtos.models import Lote

        tipo = TipoMovimentacao.objects.get(codigo="ENTRADA")
        lote = Lote.objects.create(
            produto=self.cleaned_data["produto"],
            fornecedor=self.cleaned_data["fornecedor"],
            codigo_lote=self.cleaned_data["codigo_lote"],
            data_validade=self.cleaned_data.get("data_validade"),
            quantidade_atual=0,
        )
        mov = Movimentacao.objects.create(
            lote=lote,
            usuario=usuario,
            tipo_movimentacao=tipo,
            quantidade=self.cleaned_data["quantidade"],
            data_movimento=timezone.localdate(),
            observacao=self.cleaned_data.get("observacao") or "",
        )
        return mov


class NfeXmlUploadForm(forms.Form):
    arquivo = forms.FileField(
        label="Ficheiro XML (NF-e)",
        help_text="XML autorizado (ex.: nfeProc). Tamanho máximo ~3 MB.",
        widget=forms.ClearableFileInput(attrs={"accept": ".xml,application/xml,text/xml"}),
    )

    def clean_arquivo(self):
        f = self.cleaned_data["arquivo"]
        if f.size > 3 * 1024 * 1024:
            raise forms.ValidationError("O ficheiro não pode exceder 3 MB.")
        name = (f.name or "").lower()
        if not name.endswith(".xml"):
            raise forms.ValidationError("O ficheiro deve ter extensão .xml")
        return f


class DanfeForm(forms.ModelForm):
    class Meta:
        model = Danfe
        fields = (
            "fornecedor",
            "numero",
            "serie",
            "chave_44",
            "data_emissao",
            "data_vencimento",
            "valor_total",
        )
        widgets = {
            "data_emissao": forms.DateInput(attrs={"type": "date"}),
            "data_vencimento": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        self.usuario = kwargs.pop("usuario")
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.usuario = self.usuario
        if commit:
            obj.save()
        return obj
