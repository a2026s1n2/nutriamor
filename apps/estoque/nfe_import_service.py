"""Processa dados já lidos do XML e grava DANFE, itens, lotes e movimentações."""
from __future__ import annotations

from datetime import date
from decimal import Decimal

from typing import Any

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.produtos.models import Categoria, Fornecedor, Lote, Produto

from .models import Danfe, DanfeItem, Movimentacao, TipoMovimentacao
from .nfe_xml import NfeCabecalhoParsed


def _only_digits(s: str) -> str:
    import re

    return re.sub(r"\D", "", s or "")


def encontrar_fornecedor_por_documento(documento: str) -> Fornecedor | None:
    doc = _only_digits(documento)
    if not doc:
        return None
    for f in Fornecedor.objects.filter(ativo=True).iterator():
        if _only_digits(f.documento) == doc:
            return f
    return None


def encontrar_produto_por_codigo_referencia(codigo: str) -> Produto | None:
    return Produto.objects.filter(codigo=codigo.strip()[:40], ativo=True).first()


def _data_movimento(parsed: NfeCabecalhoParsed) -> date:
    if parsed.data_emissao:
        try:
            return date.fromisoformat(parsed.data_emissao[:10])
        except ValueError:
            pass
    return timezone.localdate()


@transaction.atomic
def processar_importacao_nfe(
    *,
    usuario,
    parsed: NfeCabecalhoParsed,
    post: dict,
    categoria_padrao: Categoria | None,
) -> Danfe:
    """
    post: QueryDict com campos criar_{idx}, descricao_{idx}, categoria_{idx} (idx = índice na lista de itens em falta).
    categoria_padrao: obrigatória se existir criação de produtos.
    """
    if Danfe.objects.filter(chave_44=parsed.chave_44).exists():
        raise ValidationError("Esta NF-e (chave) já foi importada no sistema.")

    fornecedor = encontrar_fornecedor_por_documento(parsed.emit_cnpj)
    if fornecedor is None and post.get("criar_fornecedor") == "on":
        fornecedor = Fornecedor.objects.create(
            razao_social=parsed.emit_nome[:200],
            nome_fantasia="",
            documento=_only_digits(parsed.emit_cnpj)[:20],
            ativo=True,
        )
    if fornecedor is None:
        raise ValidationError(
            "Fornecedor não encontrado pelo CNPJ/CPF do emitente. "
            "Marque «Criar fornecedor a partir do XML» ou cadastre-o antes."
        )

    # Resolver produtos em falta (criação opcional por linha)
    falhas: list[tuple[int, Any]] = []
    for idx, it in enumerate(parsed.itens):
        if encontrar_produto_por_codigo_referencia(it.c_prod):
            continue
        if post.get(f"criar_{idx}") == "on":
            cat_id = post.get(f"categoria_{idx}") or (str(categoria_padrao.pk) if categoria_padrao else "")
            if not cat_id:
                raise ValidationError(
                    f"Item {it.c_prod}: escolha uma categoria ou defina a categoria padrão para novos produtos."
                )
            try:
                cat = Categoria.objects.get(pk=int(cat_id), ativo=True)
            except (Categoria.DoesNotExist, ValueError) as e:
                raise ValidationError(f"Categoria inválida para o item {it.c_prod}.") from e
            desc = (post.get(f"descricao_{idx}") or it.x_prod or it.c_prod).strip()[:255]
            try:
                Produto.objects.create(
                    categoria=cat,
                    codigo=it.c_prod[:40],
                    descricao=desc,
                    unidade_medida=(it.u_com or "UN")[:16],
                    estoque_minimo=Decimal("0"),
                    controla_validade=True,
                    ativo=True,
                )
            except IntegrityError as e:
                raise ValidationError(
                    f"Não foi possível criar o produto código «{it.c_prod}» (já existe ou dados inválidos)."
                ) from e
        else:
            falhas.append((idx, it))

    if falhas:
        lista = ", ".join(x[1].c_prod for x in falhas[:12])
        extra = "…" if len(falhas) > 12 else ""
        raise ValidationError(
            "Ainda existem produtos sem cadastro: "
            f"{lista}{extra}. Marque «Criar produto» nessas linhas (e categoria) ou cadastre-os antes."
        )

    tipo_entrada = TipoMovimentacao.objects.get(codigo="ENTRADA")
    data_mov = _data_movimento(parsed)

    danfe = Danfe.objects.create(
        fornecedor=fornecedor,
        usuario=usuario,
        numero=parsed.numero,
        serie=parsed.serie,
        chave_44=parsed.chave_44,
        data_emissao=data_mov if parsed.data_emissao else None,
        data_vencimento=None,
        valor_total=parsed.valor_total,
    )

    obs = f"Importação XML NF-e {parsed.chave_44}"

    for it in parsed.itens:
        produto = Produto.objects.get(codigo=it.c_prod[:40])
        codigo_lote = f"NF{parsed.chave_44[-12:]}-{it.n_item}"[:80]
        lote, _ = Lote.objects.get_or_create(
            produto=produto,
            fornecedor=fornecedor,
            codigo_lote=codigo_lote,
            defaults={
                "data_validade": None,
                "quantidade_atual": Decimal("0"),
            },
        )
        DanfeItem.objects.create(
            danfe=danfe,
            produto=produto,
            lote=lote,
            quantidade=it.q_com,
            valor_unitario=it.v_un_com,
            valor_item=it.v_prod,
        )
        Movimentacao.objects.create(
            lote=lote,
            usuario=usuario,
            tipo_movimentacao=tipo_entrada,
            quantidade=it.q_com,
            data_movimento=data_mov,
            observacao=obs,
        )

    return danfe
