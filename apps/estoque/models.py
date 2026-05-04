from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models


class TipoMovimentacao(models.Model):
    codigo = models.CharField(max_length=32, unique=True)
    nome = models.CharField(max_length=120)

    class Meta:
        db_table = "tipos_movimentacao"
        ordering = ["codigo"]

    def __str__(self):
        return f"{self.codigo} — {self.nome}"


class Movimentacao(models.Model):
    lote = models.ForeignKey(
        "produtos.Lote",
        on_delete=models.PROTECT,
        related_name="movimentacoes",
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="movimentacoes",
    )
    tipo_movimentacao = models.ForeignKey(
        TipoMovimentacao,
        on_delete=models.PROTECT,
        related_name="movimentacoes",
    )
    quantidade = models.DecimalField(max_digits=14, decimal_places=3)
    data_movimento = models.DateField()
    observacao = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "movimentacoes"
        ordering = ["-criado_em"]

    def __str__(self):
        return f"{self.tipo_movimentacao.codigo} {self.quantidade} — {self.lote}"


chave44_validator = RegexValidator(
    regex=r"^\d{44}$",
    message="A chave de NF-e deve ter exatamente 44 dígitos numéricos.",
)


class Danfe(models.Model):
    fornecedor = models.ForeignKey(
        "produtos.Fornecedor",
        on_delete=models.PROTECT,
        related_name="danfes",
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="danfes_registradas",
    )
    numero = models.PositiveIntegerField()
    serie = models.PositiveIntegerField(default=1)
    chave_44 = models.CharField(max_length=44, unique=True, validators=[chave44_validator])
    data_emissao = models.DateField(null=True, blank=True)
    data_vencimento = models.DateField(null=True, blank=True)
    valor_total = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    adicionado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "danfes"
        ordering = ["-adicionado_em"]

    def __str__(self):
        return f"NF {self.numero}/{self.serie}"


class DanfeItem(models.Model):
    danfe = models.ForeignKey(Danfe, on_delete=models.CASCADE, related_name="itens")
    produto = models.ForeignKey(
        "produtos.Produto",
        on_delete=models.PROTECT,
        related_name="danfe_itens",
    )
    lote = models.ForeignKey(
        "produtos.Lote",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="danfe_itens",
    )
    quantidade = models.DecimalField(max_digits=14, decimal_places=3)
    valor_unitario = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    valor_item = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    class Meta:
        db_table = "danfe_itens"

    def __str__(self):
        return f"{self.danfe_id} — {self.produto.codigo}"


class Inventario(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="inventarios",
    )
    data_inventario = models.DateField()
    observacao = models.TextField(blank=True)

    class Meta:
        db_table = "inventarios"
        ordering = ["-data_inventario"]

    def __str__(self):
        return f"Inventário {self.data_inventario}"


class InventarioItem(models.Model):
    inventario = models.ForeignKey(
        Inventario,
        on_delete=models.CASCADE,
        related_name="itens",
    )
    produto = models.ForeignKey(
        "produtos.Produto",
        on_delete=models.PROTECT,
        related_name="inventario_itens",
    )
    quantidade_sistema = models.DecimalField(max_digits=14, decimal_places=3)
    quantidade_contada = models.DecimalField(max_digits=14, decimal_places=3)
    quantidade_diferenca = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    observacao = models.TextField(blank=True)

    class Meta:
        db_table = "inventario_itens"

    def save(self, *args, **kwargs):
        self.quantidade_diferenca = self.quantidade_contada - self.quantidade_sistema
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.produto.codigo} (Δ {self.quantidade_diferenca})"
