from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import DecimalField, Sum, Value
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.views.generic import TemplateView

from apps.estoque.models import Movimentacao
from apps.produtos.models import Categoria, Fornecedor, Lote, Produto

# Coalesce(Sum(decimal), 0) exige output_field explícito no Django 5+
_QTY_FIELD = DecimalField(max_digits=14, decimal_places=3)
_ZERO_QTY = Value(Decimal("0"), output_field=_QTY_FIELD)


def _coalesce_sum_quantidade():
    return Coalesce(Sum("quantidade_atual"), _ZERO_QTY, output_field=_QTY_FIELD)


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "core/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        hoje = timezone.localdate()
        inicio_7 = hoje - timedelta(days=6)
        inicio_30 = hoje - timedelta(days=30)

        ctx["total_produtos"] = Produto.objects.filter(ativo=True).count()
        ctx["total_lotes"] = Lote.objects.count()
        ctx["mov_hoje"] = Movimentacao.objects.filter(data_movimento=hoje).count()
        ctx["total_categorias"] = Categoria.objects.filter(ativo=True).count()
        ctx["total_fornecedores"] = Fornecedor.objects.filter(ativo=True).count()

        stock = Lote.objects.aggregate(t=_coalesce_sum_quantidade())["t"] or 0
        ctx["stock_total_unidades"] = stock

        ctx["lotes_vencer_30d"] = Lote.objects.filter(
            data_validade__gte=hoje,
            data_validade__lte=hoje + timedelta(days=30),
            quantidade_atual__gt=0,
        ).count()

        ctx["mov_7d_total"] = Movimentacao.objects.filter(
            data_movimento__gte=inicio_7,
            data_movimento__lte=hoje,
        ).count()

        ctx["entradas_30d"] = Movimentacao.objects.filter(
            data_movimento__gte=inicio_30,
            tipo_movimentacao__codigo="ENTRADA",
        ).count()
        ctx["saidas_30d"] = Movimentacao.objects.filter(
            data_movimento__gte=inicio_30,
            tipo_movimentacao__codigo="SAIDA",
        ).count()

        mov_por_dia = []
        max_bar = 1
        for i in range(6, -1, -1):
            d = hoje - timedelta(days=i)
            n = Movimentacao.objects.filter(data_movimento=d).count()
            max_bar = max(max_bar, n)
            mov_por_dia.append({"data": d, "total": n, "label": d.strftime("%d/%m")})
        ctx["mov_por_dia"] = mov_por_dia
        ctx["mov_chart_max"] = max_bar

        # Top produtos por volume em lotes (proxy de “peso” no armazém)
        top_prod = (
            Lote.objects.values("produto__codigo", "produto__descricao")
            .annotate(vol=_coalesce_sum_quantidade())
            .order_by("-vol")[:5]
        )
        ctx["top_produtos_volume"] = list(top_prod)

        # Últimas movimentações (mini feed)
        ctx["ultimas_movs"] = Movimentacao.objects.select_related(
            "tipo_movimentacao", "lote__produto", "usuario"
        ).order_by("-criado_em")[:8]

        abaixo = []
        for p in Produto.objects.filter(ativo=True):
            total = (
                Lote.objects.filter(produto=p).aggregate(t=_coalesce_sum_quantidade())["t"]
                or 0
            )
            if total < p.estoque_minimo:
                abaixo.append({"produto": p, "saldo": total})
        ctx["abaixo_minimo"] = abaixo[:10]
        ctx["data_label"] = hoje.strftime("%d/%m/%Y")
        return ctx
