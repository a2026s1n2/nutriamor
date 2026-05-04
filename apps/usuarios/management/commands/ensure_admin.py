from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from apps.usuarios.models import Perfil

User = get_user_model()


class Command(BaseCommand):
    help = (
        "Cria ou atualiza um utilizador com perfil ADMIN (staff + superuser). "
        "Garante o perfil ADMIN na tabela perfis. Corra depois de migrate (e idealmente seed_base)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--email",
            required=True,
            help="E-mail de login (ex.: admin@nutriamor.cienciadedadosunivesp.app.br)",
        )
        parser.add_argument(
            "--password",
            required=True,
            help="Palavra-passe (use aspas se tiver caracteres especiais)",
        )
        parser.add_argument(
            "--nome",
            default="Administrador",
            help="Nome apresentado no sistema (default: Administrador)",
        )

    def handle(self, *args, **options):
        email = options["email"].strip().lower()
        password = options["password"]
        nome = options["nome"].strip()

        perfil, _ = Perfil.objects.get_or_create(
            codigo="ADMIN",
            defaults={"nome": "Administrador"},
        )

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "username": email,
                "nome": nome,
                "is_staff": True,
                "is_superuser": True,
                "perfil": perfil,
            },
        )
        if not created:
            user.nome = nome or user.nome
            user.is_staff = True
            user.is_superuser = True
            user.perfil = perfil
            if not user.username:
                user.username = email

        user.set_password(password)
        user.save()

        self.stdout.write(
            self.style.SUCCESS(
                f"Administrador pronto: {email} (novo={'sim' if created else 'não'}, palavra-passe atualizada)"
            )
        )
