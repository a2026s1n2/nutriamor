from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


class EscritaNecessariaMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Bloqueia perfil CONSULTA de alterar dados (documentação: perfis de acesso)."""

    def test_func(self):
        u = self.request.user
        if not u.is_authenticated:
            return False
        if getattr(u, "is_superuser", False):
            return True
        return u.pode_escrita
