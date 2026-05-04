from django.urls import path

from . import views

app_name = "estoque"

urlpatterns = [
    path("movimentacoes/", views.MovimentacaoListView.as_view(), name="movimentacao_list"),
    path("movimentacoes/nova/", views.MovimentacaoCreateView.as_view(), name="movimentacao_create"),
    path("entrada-sem-nota/", views.EntradaSemNotaView.as_view(), name="entrada_sem_nota"),
    path("danfes/", views.DanfeListView.as_view(), name="danfe_list"),
    path("danfes/nova/", views.DanfeCreateView.as_view(), name="danfe_create"),
    path("danfes/importar-xml/", views.NfeXmlUploadView.as_view(), name="nfe_xml_upload"),
    path("danfes/importar-xml/revisao/<str:token>/", views.NfeXmlReviewView.as_view(), name="nfe_xml_review"),
]
