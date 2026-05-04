from django.db import models


class Categoria(models.Model):
    nome = models.CharField(max_length=120)
    descricao = models.TextField(blank=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        db_table = "categorias"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class TipoFornecedor(models.Model):
    nome = models.CharField(max_length=120)

    class Meta:
        db_table = "tipos_fornecedor"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class Fornecedor(models.Model):
    tipo_fornecedor = models.ForeignKey(
        TipoFornecedor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="fornecedores",
    )
    razao_social = models.CharField(max_length=200)
    nome_fantasia = models.CharField(max_length=200, blank=True)
    documento = models.CharField(max_length=20, blank=True, help_text="CNPJ / CPF / outro")
    telefone = models.CharField(max_length=32, blank=True)
    email = models.EmailField(blank=True)
    cidade = models.CharField(max_length=120, blank=True)
    uf = models.CharField(max_length=2, blank=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        db_table = "fornecedores"
        ordering = ["razao_social"]

    def __str__(self):
        return self.razao_social


class Produto(models.Model):
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name="produtos",
    )
    codigo = models.CharField(max_length=40, unique=True)
    descricao = models.CharField(max_length=255)
    unidade_medida = models.CharField(max_length=16, default="UN")
    estoque_minimo = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    controla_validade = models.BooleanField(default=True)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "produtos"
        ordering = ["descricao"]

    def __str__(self):
        return f"{self.codigo} — {self.descricao}"


class Lote(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT, related_name="lotes")
    fornecedor = models.ForeignKey(
        Fornecedor,
        on_delete=models.PROTECT,
        related_name="lotes",
    )
    codigo_lote = models.CharField(max_length=80)
    data_validade = models.DateField(null=True, blank=True)
    quantidade_atual = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "lotes"
        ordering = ["-criado_em"]
        indexes = [
            models.Index(fields=["produto", "data_validade"], name="idx_lote_prod_valid"),
        ]

    def __str__(self):
        return f"{self.codigo_lote} ({self.produto.codigo})"
