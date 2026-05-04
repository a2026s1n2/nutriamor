"""
Leitura mínima de XML de NF-e (modelo comum 4.00) para importação.
Não substitui validação fiscal — apenas extrai dados para o fluxo de stock.
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any


class NfeXmlErro(Exception):
    pass


@dataclass
class NfeItemParsed:
    n_item: str
    c_prod: str
    x_prod: str
    u_com: str
    q_com: Decimal
    v_un_com: Decimal
    v_prod: Decimal


@dataclass
class NfeCabecalhoParsed:
    chave_44: str
    numero: int
    serie: int
    emit_cnpj: str
    emit_nome: str
    data_emissao: str | None  # YYYY-MM-DD
    valor_total: Decimal
    itens: list[NfeItemParsed]


def _local(tag: str) -> str:
    return tag.split("}", 1)[-1] if "}" in tag else tag


def _find_first(root: ET.Element, name: str) -> ET.Element | None:
    for el in root.iter():
        if _local(el.tag) == name:
            return el
    return None


def _find_child(parent: ET.Element, name: str) -> ET.Element | None:
    for ch in parent:
        if _local(ch.tag) == name:
            return ch
    return None


def _text(el: ET.Element | None) -> str:
    if el is None or el.text is None:
        return ""
    return el.text.strip()


def _only_digits(s: str) -> str:
    return re.sub(r"\D", "", s or "")


def _dec(s: str, default: str = "0") -> Decimal:
    try:
        return Decimal((s or default).replace(",", "."))
    except (InvalidOperation, ValueError):
        return Decimal(default)


def extrair_chave_44(inf_nfe: ET.Element) -> str:
    raw = (inf_nfe.get("Id") or "").strip()
    m = re.search(r"(\d{44})", raw)
    if m:
        return m.group(1)
    m2 = re.search(r"(\d{44})", "".join(inf_nfe.itertext()))
    if m2:
        return m2.group(1)
    raise NfeXmlErro("Não foi possível localizar a chave de 44 dígitos (atributo Id em infNFe).")


def parse_nfe_xml_bytes(content: bytes) -> NfeCabecalhoParsed:
    if not content or len(content) > 3_500_000:
        raise NfeXmlErro("Ficheiro XML vazio ou demasiado grande (máx. ~3,5 MB).")

    try:
        root = ET.fromstring(content)
    except ET.ParseError as e:
        raise NfeXmlErro(f"XML inválido: {e}") from e

    nfe = _find_first(root, "NFe")
    if nfe is None:
        raise NfeXmlErro("Elemento NFe não encontrado. Confirme se é um XML de NF-e autorizada (nfeProc).")

    inf_nfe = _find_child(nfe, "infNFe")
    if inf_nfe is None:
        raise NfeXmlErro("Elemento infNFe não encontrado.")

    chave = extrair_chave_44(inf_nfe)

    ide = _find_child(inf_nfe, "ide")
    if ide is None:
        raise NfeXmlErro("Elemento ide não encontrado.")
    n_nf = int(_text(_find_child(ide, "nNF")) or "0")
    serie = int(_text(_find_child(ide, "serie")) or "0")
    dh_emi = _text(_find_child(ide, "dhEmi")) or _text(_find_child(ide, "dEmi"))
    data_emissao: str | None = None
    if dh_emi and len(dh_emi) >= 10:
        data_emissao = dh_emi[:10]

    emit = _find_child(inf_nfe, "emit")
    if emit is None:
        raise NfeXmlErro("Elemento emit (fornecedor) não encontrado.")
    cnpj = _only_digits(_text(_find_child(emit, "CNPJ")))
    cpf = _only_digits(_text(_find_child(emit, "CPF")))
    emit_doc = cnpj or cpf
    if not emit_doc:
        raise NfeXmlErro("CNPJ/CPF do emitente não encontrado no XML.")
    emit_nome = _text(_find_child(emit, "xNome")) or _text(_find_child(emit, "xFant")) or "Emitente NF-e"

    itens: list[NfeItemParsed] = []
    for det in inf_nfe:
        if _local(det.tag) != "det":
            continue
        n_item = det.get("nItem") or str(len(itens) + 1)
        prod = _find_child(det, "prod")
        if prod is None:
            continue
        c_prod = (_text(_find_child(prod, "cProd")) or "")[:40]
        x_prod = (_text(_find_child(prod, "xProd")) or "")[:255]
        u_com = (_text(_find_child(prod, "uCom")) or "UN")[:16]
        q_com = _dec(_text(_find_child(prod, "qCom")), "0")
        v_un = _dec(_text(_find_child(prod, "vUnCom")), "0")
        v_prod = _dec(_text(_find_child(prod, "vProd")), "0")
        if not c_prod:
            continue
        itens.append(
            NfeItemParsed(
                n_item=n_item,
                c_prod=c_prod,
                x_prod=x_prod,
                u_com=u_com,
                q_com=q_com,
                v_un_com=v_un,
                v_prod=v_prod,
            )
        )

    if not itens:
        raise NfeXmlErro("Nenhum item de produto (det/prod) encontrado no XML.")

    valor_total = Decimal("0")
    total_el = _find_child(inf_nfe, "total")
    if total_el is not None:
        icms_tot = _find_child(total_el, "ICMSTot")
        if icms_tot is not None:
            v_nf = _text(_find_child(icms_tot, "vNF"))
            if v_nf:
                valor_total = _dec(v_nf, "0")
    if valor_total == 0:
        valor_total = sum((i.v_prod for i in itens), Decimal("0"))

    return NfeCabecalhoParsed(
        chave_44=chave,
        numero=n_nf,
        serie=serie,
        emit_cnpj=emit_doc,
        emit_nome=emit_nome[:200],
        data_emissao=data_emissao,
        valor_total=valor_total,
        itens=itens,
    )


def parsed_to_dict(p: NfeCabecalhoParsed) -> dict[str, Any]:
    return {
        "chave_44": p.chave_44,
        "numero": p.numero,
        "serie": p.serie,
        "emit_cnpj": p.emit_cnpj,
        "emit_nome": p.emit_nome,
        "data_emissao": p.data_emissao,
        "valor_total": str(p.valor_total),
        "itens": [
            {
                "n_item": i.n_item,
                "c_prod": i.c_prod,
                "x_prod": i.x_prod,
                "u_com": i.u_com,
                "q_com": str(i.q_com),
                "v_un_com": str(i.v_un_com),
                "v_prod": str(i.v_prod),
            }
            for i in p.itens
        ],
    }


def dict_to_parsed(d: dict[str, Any]) -> NfeCabecalhoParsed:
    itens = [
        NfeItemParsed(
            n_item=str(x["n_item"]),
            c_prod=x["c_prod"],
            x_prod=x["x_prod"],
            u_com=x["u_com"],
            q_com=Decimal(x["q_com"]),
            v_un_com=Decimal(x["v_un_com"]),
            v_prod=Decimal(x["v_prod"]),
        )
        for x in d["itens"]
    ]
    return NfeCabecalhoParsed(
        chave_44=d["chave_44"],
        numero=int(d["numero"]),
        serie=int(d["serie"]),
        emit_cnpj=d["emit_cnpj"],
        emit_nome=d["emit_nome"],
        data_emissao=d.get("data_emissao"),
        valor_total=Decimal(d["valor_total"]),
        itens=itens,
    )
