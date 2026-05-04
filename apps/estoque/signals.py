from decimal import Decimal

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Movimentacao


@receiver(post_save, sender=Movimentacao)
def atualizar_saldo_lote(sender, instance: Movimentacao, created: bool, **kwargs):
    """Após nova movimentação, atualiza `Lote.quantidade_atual` conforme o código do tipo (documentação)."""
    if not created:
        return
    codigo = instance.tipo_movimentacao.codigo.upper()
    q = instance.quantidade

    from apps.produtos.models import Lote

    with transaction.atomic():
        lote = Lote.objects.select_for_update().get(pk=instance.lote_id)
        atual = lote.quantidade_atual or Decimal("0")
        if codigo == "ENTRADA":
            novo = atual + q
        elif codigo in ("SAIDA", "PERDA"):
            novo = atual - q
        elif codigo == "AJUSTE":
            novo = atual + q
        else:
            novo = atual + q
        if novo < 0:
            novo = Decimal("0")
        lote.quantidade_atual = novo
        lote.save(update_fields=["quantidade_atual"])
