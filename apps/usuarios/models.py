from typing import Optional

from django.contrib.auth.models import AbstractUser
from django.db import models


class Perfil(models.Model):
    """Perfis de acesso (documentação: Admin, Estoquista, Consulta)."""

    nome = models.CharField(max_length=64)
    codigo = models.CharField(
        max_length=32,
        unique=True,
        help_text="Ex.: ADMIN, ESTOQUISTA, CONSULTA — usado em permissões de tela.",
    )

    class Meta:
        db_table = "perfis"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class Usuario(AbstractUser):
    """Utilizador do sistema alinhado ao DER (extensão do modelo de auth do Django)."""

    nome = models.CharField(max_length=150)
    perfil = models.ForeignKey(
        Perfil,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="usuarios",
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    email = models.EmailField(unique=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nome"]

    class Meta(AbstractUser.Meta):
        db_table = "usuarios"

    def __str__(self):
        return self.nome or self.email

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email
        super().save(*args, **kwargs)

    def codigo_perfil(self) -> Optional[str]:
        return self.perfil.codigo if self.perfil_id else None

    @property
    def pode_escrita(self) -> bool:
        c = self.codigo_perfil()
        return c in ("ADMIN", "ESTOQUISTA") or self.is_superuser

    @property
    def somente_leitura(self) -> bool:
        return self.codigo_perfil() == "CONSULTA" and not self.is_superuser
