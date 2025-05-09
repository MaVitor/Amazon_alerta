from django.contrib import admin
from .models import Produto, HistoricoPreco, Contato, Alerta

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'preco_atual', 'preco_alvo', 'ultimo_check', 'ativo')
    list_filter = ('ativo',)
    search_fields = ('nome', 'url')

@admin.register(HistoricoPreco)
class HistoricoPrecoAdmin(admin.ModelAdmin):
    list_display = ('produto', 'preco', 'data')
    list_filter = ('produto',)
    date_hierarchy = 'data'

@admin.register(Contato)
class ContatoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'telefone', 'ativo')
    list_filter = ('ativo',)
    search_fields = ('nome', 'telefone')

@admin.register(Alerta)
class AlertaAdmin(admin.ModelAdmin):
    list_display = ('produto', 'contato', 'data_envio', 'preco_no_momento')
    list_filter = ('contato', 'produto')
    date_hierarchy = 'data_envio'
