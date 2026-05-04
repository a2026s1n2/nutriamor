from django.core.management.base import BaseCommand

from apps.estoque.models import TipoMovimentacao
from apps.usuarios.models import Perfil
from apps.produtos.models import TipoFornecedor


class Command(BaseCommand):
    help = "Cria perfis, tipos de movimentação e tipos de fornecedor iniciais (documentação NutriAmor)."

    def handle(self, *args, **options):
        perfis = [
            ("Administrador", "ADMIN"),
            ("Estoquista", "ESTOQUISTA"),
            ("Consulta", "CONSULTA"),
        ]
        for nome, codigo in perfis:
            Perfil.objects.get_or_create(codigo=codigo, defaults={"nome": nome})

        movs = [
            ("ENTRADA", "Entrada de stock"),
            ("SAIDA", "Saída / consumo"),
            ("AJUSTE", "Ajuste de inventário"),
            ("PERDA", "Perda / vencimento"),
        ]
        for codigo, nome in movs:
            TipoMovimentacao.objects.get_or_create(codigo=codigo, defaults={"nome": nome})

        tipos_f = [
            "Indústria / distribuidor",
            "Comércio local",
            "Doador / ONG",
            "Outro",
        ]
        for nome in tipos_f:
            TipoFornecedor.objects.get_or_create(nome=nome)

        self.stdout.write(self.style.SUCCESS("Catálogos base criados ou já existentes."))
