from django.contrib import messages
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, FormView, ListView

import uuid

from apps.core.mixins import EscritaNecessariaMixin
from apps.produtos.models import Categoria

from .forms import DanfeForm, MovimentacaoEntradaRapidaForm, MovimentacaoForm, NfeXmlUploadForm
from .models import Danfe, Movimentacao, TipoMovimentacao
from .nfe_import_service import encontrar_fornecedor_por_documento, encontrar_produto_por_codigo_referencia, processar_importacao_nfe
from .nfe_xml import NfeXmlErro, dict_to_parsed, parse_nfe_xml_bytes, parsed_to_dict

NFE_XML_CACHE = "nfe_xml_import:"
NFE_XML_TTL = 3600


class MovimentacaoListView(ListView):
    model = Movimentacao
    template_name = "estoque/movimentacao_list.html"
    context_object_name = "itens"
    paginate_by = 30


class MovimentacaoCreateView(EscritaNecessariaMixin, CreateView):
    model = Movimentacao
    form_class = MovimentacaoForm
    template_name = "estoque/movimentacao_form.html"
    success_url = reverse_lazy("estoque:movimentacao_list")

    def form_valid(self, form):
        with transaction.atomic():
            return super().form_valid(form)

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["usuario"] = self.request.user
        return kw

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["titulo"] = "Nova movimentação (lote existente)"
        ctx["tipos"] = TipoMovimentacao.objects.all()
        return ctx


class EntradaSemNotaView(EscritaNecessariaMixin, FormView):
    template_name = "estoque/entrada_sem_nota.html"
    form_class = MovimentacaoEntradaRapidaForm
    success_url = reverse_lazy("estoque:movimentacao_list")

    def form_valid(self, form):
        with transaction.atomic():
            form.save_movimentacao(self.request.user)
        messages.success(
            self.request,
            "Entrada sem nota registrada (lote criado + movimentação ENTRADA).",
        )
        return super().form_valid(form)


class DanfeCreateView(EscritaNecessariaMixin, CreateView):
    model = Danfe
    form_class = DanfeForm
    template_name = "estoque/danfe_form.html"
    success_url = reverse_lazy("estoque:danfe_list")

    def form_valid(self, form):
        with transaction.atomic():
            return super().form_valid(form)

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["usuario"] = self.request.user
        return kw


class DanfeListView(ListView):
    model = Danfe
    template_name = "estoque/danfe_list.html"
    context_object_name = "itens"


class NfeXmlUploadView(EscritaNecessariaMixin, FormView):
    template_name = "estoque/nfe_xml_upload.html"
    form_class = NfeXmlUploadForm

    def form_valid(self, form):
        f = form.cleaned_data["arquivo"]
        raw = f.read()
        try:
            parsed = parse_nfe_xml_bytes(raw)
        except NfeXmlErro as e:
            form.add_error("arquivo", str(e))
            return self.form_invalid(form)
        if Danfe.objects.filter(chave_44=parsed.chave_44).exists():
            form.add_error("arquivo", "Esta NF-e (chave) já existe no sistema.")
            return self.form_invalid(form)
        token = uuid.uuid4().hex
        cache.set(NFE_XML_CACHE + token, parsed_to_dict(parsed), NFE_XML_TTL)
        return redirect("estoque:nfe_xml_review", token=token)


class NfeXmlReviewView(EscritaNecessariaMixin, View):
    template_name = "estoque/nfe_xml_review.html"

    def _context(self, token, parsed, post=None):
        q = post if post is not None else {}
        fornecedor = encontrar_fornecedor_por_documento(parsed.emit_cnpj)
        pre_criar_forn = q.get("criar_fornecedor") == "on"
        pre_cat_padrao = (q.get("categoria_padrao") or "").strip()

        linhas = []
        for idx, it in enumerate(parsed.itens):
            prod = encontrar_produto_por_codigo_referencia(it.c_prod)
            linhas.append(
                {
                    "idx": idx,
                    "item": it,
                    "produto": prod,
                    "ok": prod is not None,
                    "prefill_desc": (q.get(f"descricao_{idx}") or it.x_prod or "")[:255],
                    "prefill_cat": (q.get(f"categoria_{idx}") or "").strip(),
                    "prefill_criar": q.get(f"criar_{idx}") == "on",
                }
            )
        return {
            "token": token,
            "parsed": parsed,
            "fornecedor_xml_doc": parsed.emit_cnpj,
            "fornecedor_xml_nome": parsed.emit_nome,
            "fornecedor_match": fornecedor,
            "linhas": linhas,
            "categorias": Categoria.objects.filter(ativo=True).order_by("nome"),
            "pre_criar_forn": pre_criar_forn,
            "pre_cat_padrao": pre_cat_padrao,
        }

    def get(self, request, token):
        data = cache.get(NFE_XML_CACHE + token)
        if not data:
            raise Http404("Importação expirou ou não existe. Envie o XML novamente.")
        parsed = dict_to_parsed(data)
        return render(request, self.template_name, self._context(token, parsed))

    def post(self, request, token):
        data = cache.get(NFE_XML_CACHE + token)
        if not data:
            raise Http404("Importação expirou ou não existe.")
        parsed = dict_to_parsed(data)
        cat_padrao = None
        cp = request.POST.get("categoria_padrao")
        if cp:
            try:
                cat_padrao = Categoria.objects.get(pk=int(cp), ativo=True)
            except (Categoria.DoesNotExist, ValueError):
                messages.error(request, "Categoria padrão inválida.")
                return render(request, self.template_name, self._context(token, parsed, request.POST))

        try:
            processar_importacao_nfe(
                usuario=request.user,
                parsed=parsed,
                post=request.POST,
                categoria_padrao=cat_padrao,
            )
        except ValidationError as e:
            for msg in e.messages:
                messages.error(request, msg)
            return render(request, self.template_name, self._context(token, parsed, request.POST))

        cache.delete(NFE_XML_CACHE + token)
        messages.success(
            request,
            "NF-e importada: DANFE, itens, lotes e movimentações de entrada criados.",
        )
        return redirect("estoque:danfe_list")
