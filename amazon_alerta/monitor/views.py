from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Count, Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from decimal import Decimal
import json
import os
from django.conf import settings

from .models import Produto, HistoricoPreco, Contato, Alerta
from .scraper import AmazonScraper
from .whatsapp import WhatsAppNotifier
from .forms import ProdutoForm, ContatoForm

# Template filter para calcular a diferença entre dois valores
from django.template.defaulttags import register

@register.filter
def sub(value, arg):
    return value - arg

@register.filter
def abs(value):
    return abs(value)

# Dashboard
@login_required
def dashboard(request):
    produtos = Produto.objects.filter(ativo=True)
    contatos = Contato.objects.filter(ativo=True)
    alertas = Alerta.objects.all().order_by('-data_envio')[:5]
    
    # Dados para o gráfico
    produtos_com_historico = []
    chart_dates = []
    
    try:
        # Pega os 5 produtos mais recentes com histórico
        produtos_recentes = Produto.objects.filter(
            historico__isnull=False
        ).distinct().order_by('-ultimo_check')[:5]
        
        if produtos_recentes.exists():
            # Pega as últimas 10 datas de verificação
            historicos = HistoricoPreco.objects.order_by('-data')[:10]
            
            if historicos.exists():
                # Formata as datas para o gráfico
                chart_dates = [h.data.strftime('%d/%m/%Y') for h in historicos]
                
                for produto in produtos_recentes:
                    precos = []
                    for historico in historicos:
                        try:
                            # Busca o histórico deste produto nesta data
                            hist_produto = HistoricoPreco.objects.filter(
                                produto=produto,
                                data__date=historico.data.date()
                            ).first()
                            
                            if hist_produto:
                                precos.append(float(hist_produto.preco))
                            else:
                                precos.append(None)
                        except Exception as e:
                            print(f"Erro ao processar histórico: {e}")
                            precos.append(None)
                    
                    # Adiciona os dados deste produto
                    produtos_com_historico.append({
                        'nome': produto.nome,
                        'precos': json.dumps(precos)
                    })
    except Exception as e:
        print(f"Erro ao preparar dados do gráfico: {e}")
    
    context = {
        'produtos': produtos,
        'contatos': contatos,
        'alertas': alertas,
        'total_produtos': produtos.count(),
        'total_contatos': contatos.count(),
        'total_historico': HistoricoPreco.objects.count(),
        'total_alertas': Alerta.objects.count(),
        'produtos_com_historico': produtos_com_historico,
        'chart_dates': json.dumps(chart_dates) if chart_dates else "[]",
    }
    
    return render(request, 'monitor/dashboard.html', context)

# Produto Views
class ProdutoListView(LoginRequiredMixin, ListView):
    model = Produto
    template_name = 'monitor/produto_list.html'
    context_object_name = 'produtos'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Produto.objects.all()
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(nome__icontains=q) | Q(url__icontains=q)
            )
        return queryset

class ProdutoDetailView(LoginRequiredMixin, DetailView):
    model = Produto
    template_name = 'monitor/produto_detail.html'
    context_object_name = 'produto'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        produto = self.get_object()
        
        # Histórico de preços
        context['historico'] = HistoricoPreco.objects.filter(
            produto=produto
        ).order_by('-data')[:20]
        
        # Alertas enviados
        context['alertas'] = Alerta.objects.filter(
            produto=produto
        ).order_by('-data_envio')
        
        # Contatos ativos para envio de notificação de teste
        context['contatos'] = Contato.objects.filter(ativo=True)
        
        return context

class ProdutoCreateView(LoginRequiredMixin, CreateView):
    model = Produto
    form_class = ProdutoForm
    template_name = 'monitor/produto_form.html'
    success_url = reverse_lazy('produto_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Produto cadastrado com sucesso!')
        return super().form_valid(form)

class ProdutoUpdateView(LoginRequiredMixin, UpdateView):
    model = Produto
    form_class = ProdutoForm
    template_name = 'monitor/produto_form.html'
    
    def get_success_url(self):
        return reverse_lazy('produto_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Produto atualizado com sucesso!')
        return super().form_valid(form)

class ProdutoDeleteView(LoginRequiredMixin, DeleteView):
    model = Produto
    template_name = 'monitor/produto_confirm_delete.html'
    context_object_name = 'produto'
    success_url = reverse_lazy('produto_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Produto excluído com sucesso!')
        return super().delete(request, *args, **kwargs)

# Contato Views
class ContatoListView(LoginRequiredMixin, ListView):
    model = Contato
    template_name = 'monitor/contato_list.html'
    context_object_name = 'contatos'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Contato.objects.annotate(alertas_count=Count('alerta'))
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(nome__icontains=q) | Q(telefone__icontains=q)
            )
        return queryset

class ContatoDetailView(LoginRequiredMixin, DetailView):
    model = Contato
    template_name = 'monitor/contato_detail.html'
    context_object_name = 'contato'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        contato = self.get_object()
        
        # Alertas enviados
        context['alertas'] = Alerta.objects.filter(
            contato=contato
        ).order_by('-data_envio')
        
        # Produtos com preço atual para envio de notificação de teste
        context['produtos_com_preco'] = Produto.objects.filter(
            ativo=True, 
            preco_atual__isnull=False
        )
        
        return context

class ContatoCreateView(LoginRequiredMixin, CreateView):
    model = Contato
    form_class = ContatoForm
    template_name = 'monitor/contato_form.html'
    success_url = reverse_lazy('contato_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Contato cadastrado com sucesso!')
        return super().form_valid(form)

class ContatoUpdateView(LoginRequiredMixin, UpdateView):
    model = Contato
    form_class = ContatoForm
    template_name = 'monitor/contato_form.html'
    
    def get_success_url(self):
        return reverse_lazy('contato_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Contato atualizado com sucesso!')
        return super().form_valid(form)

class ContatoDeleteView(LoginRequiredMixin, DeleteView):
    model = Contato
    template_name = 'monitor/contato_confirm_delete.html'
    context_object_name = 'contato'
    success_url = reverse_lazy('contato_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Contato excluído com sucesso!')
        return super().delete(request, *args, **kwargs)

# Histórico Views
class HistoricoListView(LoginRequiredMixin, ListView):
    model = HistoricoPreco
    template_name = 'monitor/historico_list.html'
    context_object_name = 'historico'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = HistoricoPreco.objects.all().order_by('-data')
        
        # Filtra por produto
        produto_id = self.request.GET.get('produto')
        if produto_id:
            queryset = queryset.filter(produto_id=produto_id)
        
        # Adiciona variação de preço
        for i, item in enumerate(queryset):
            if i < len(queryset) - 1:
                next_item = queryset[i + 1]
                if item.produto_id == next_item.produto_id:
                    item.variacao = float(item.preco) - float(next_item.preco)
                else:
                    item.variacao = None
            else:
                item.variacao = None
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Lista de produtos para o filtro
        context['produtos'] = Produto.objects.all()
        
        # Dados para o gráfico
        produto_id = self.request.GET.get('produto')
        if produto_id:
            historico = HistoricoPreco.objects.filter(
                produto_id=produto_id
            ).order_by('data')[:30]
            
            if historico:
                context['chart_data'] = {
                    'dates': [h.data.strftime('%d/%m/%Y') for h in historico],
                    'prices': [float(h.preco) for h in historico]
                }
        
        return context

# Alerta Views
class AlertaListView(LoginRequiredMixin, ListView):
    model = Alerta
    template_name = 'monitor/alerta_list.html'
    context_object_name = 'alertas'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Alerta.objects.all().order_by('-data_envio')
        
        filtro = self.request.GET.get('filtro')
        q = self.request.GET.get('q')
        
        if filtro and q:
            if filtro == 'produto':
                queryset = queryset.filter(produto__nome__icontains=q)
            elif filtro == 'contato':
                queryset = queryset.filter(contato__nome__icontains=q)
        
        return queryset

# Ações
@login_required
def check_price(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)
    
    scraper = AmazonScraper()
    success, price = scraper.update_product_price(produto_id)
    
    if success:
        messages.success(request, f'Preço atualizado com sucesso! Novo preço: R$ {price}')
    else:
        messages.error(request, 'Não foi possível atualizar o preço. Tente novamente mais tarde.')
    
    return redirect('produto_detail', pk=produto_id)

@login_required
def check_all_prices(request):
    scraper = AmazonScraper()
    results = scraper.check_all_products()
    
    # Conta os produtos verificados com sucesso
    success_count = sum(1 for result in results if result['success'])
    
    if success_count > 0:
        messages.success(request, f'Verificados {len(results)} produtos, {success_count} com sucesso.')
    else:
        messages.warning(request, f'Verificados {len(results)} produtos, mas nenhum foi atualizado com sucesso.')
    
    # Verifica produtos com preço abaixo do alvo
    produtos = Produto.objects.filter(ativo=True, preco_atual__isnull=False)
    alertas_count = 0
    
    for produto in produtos:
        if produto.preco_atual <= produto.preco_alvo:
            notifier = WhatsAppNotifier()
            if notifier.notify_price_drop(produto.id):
                alertas_count += 1
    
    if alertas_count > 0:
        messages.info(request, f'Enviados {alertas_count} alertas para produtos abaixo do preço alvo.')
    
    return redirect('dashboard')

@login_required
def send_test_notification(request, produto_id, contato_id):
    produto = get_object_or_404(Produto, id=produto_id)
    contato = get_object_or_404(Contato, id=contato_id)
    
    if not produto.preco_atual:
        messages.error(request, 'O produto não tem um preço atual. Atualize o preço primeiro.')
        return redirect('produto_detail', pk=produto_id)
    
    notifier = WhatsAppNotifier()
    success = notifier.send_notification(contato, produto, produto.preco_atual)
    
    if success:
        messages.success(request, f'Notificação de teste enviada com sucesso para {contato.nome}!')
    else:
        messages.error(request, 'Não foi possível enviar a notificação. Verifique o console para mais detalhes.')
    
    # Redireciona de volta para a página de origem
    referer = request.META.get('HTTP_REFERER')
    if referer and '/produto/' in referer:
        return redirect('produto_detail', pk=produto_id)
    elif referer and '/contato/' in referer:
        return redirect('contato_detail', pk=contato_id)
    else:
        return redirect('dashboard')

@login_required
def whatsapp_auth(request):
    """Página de instruções para autenticação do WhatsApp na versão simplificada"""
    return render(request, 'monitor/whatsapp_auth.html')

@login_required
def test_scraper(request):
    """Testa a conexão com a ScraperAPI"""
    if not hasattr(settings, 'SCRAPER_API_KEY') or not settings.SCRAPER_API_KEY:
        return JsonResponse({
            'success': False,
            'message': 'A chave da API ScraperAPI não está configurada!'
        })
    
    try:
        import requests
        
        # URL de teste simples
        test_url = "https://www.amazon.com.br/dp/B0BZ418DCW"  # URL de exemplo
        
        # Parâmetros para a ScraperAPI
        params = {
            'api_key': settings.SCRAPER_API_KEY,
            'url': test_url,
        }
        
        # Faz a requisição
        response = requests.get("https://api.scraperapi.com", params=params)
        
        if response.status_code == 200:
            return JsonResponse({
                'success': True,
                'message': 'Conexão com a ScraperAPI estabelecida com sucesso!',
                'status_code': response.status_code
            })
        else:
            return JsonResponse({
                'success': False,
                'message': f'Erro ao conectar com a ScraperAPI. Status code: {response.status_code}',
                'response': response.text[:500]  # Primeiros 500 caracteres da resposta
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao testar a conexão: {str(e)}'
        })
