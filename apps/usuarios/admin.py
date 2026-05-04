from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import Perfil, Usuario


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ("nome", "codigo")


@admin.register(Usuario)
class UsuarioAdmin(DjangoUserAdmin):
    ordering = ("email",)
    list_display = ("email", "nome", "perfil", "is_staff", "is_active")
    list_filter = ("perfil", "is_staff", "is_active")
    search_fields = ("email", "nome", "username")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Dados", {"fields": ("nome", "perfil", "username")}),
        ("Permissões", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Datas", {"fields": ("last_login", "date_joined", "criado_em")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "nome", "perfil", "password1", "password2", "is_staff", "is_superuser"),
            },
        ),
    )
    readonly_fields = ("criado_em", "last_login", "date_joined")
    filter_horizontal = ("groups", "user_permissions")
