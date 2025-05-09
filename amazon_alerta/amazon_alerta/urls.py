from django.contrib import admin
from django.urls import path
from monitor import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Produtos
    path('produtos/', views.ProdutoListView.as_view(), name='produto_list'),
    path('produtos/novo/', views.ProdutoCreateView.as_view(), name='produto_create'),
    path('produtos/<int:pk>/', views.ProdutoDetailView.as_view(), name='produto_detail'),
    path('produtos/<int:pk>/editar/', views.ProdutoUpdateView.as_view(), name='produto_update'),
    path('produtos/<int:pk>/excluir/', views.ProdutoDeleteView.as_view(), name='produto_delete'),
    
    # Contatos
    path('contatos/', views.ContatoListView.as_view(), name='contato_list'),
    path('contatos/novo/', views.ContatoCreateView.as_view(), name='contato_create'),
    path('contatos/<int:pk>/', views.ContatoDetailView.as_view(), name='contato_detail'),
    path('contatos/<int:pk>/editar/', views.ContatoUpdateView.as_view(), name='contato_update'),
    path('contatos/<int:pk>/excluir/', views.ContatoDeleteView.as_view(), name='contato_delete'),
    
    # Histórico
    path('historico/', views.HistoricoListView.as_view(), name='historico_list'),
    
    # Alertas
    path('alertas/', views.AlertaListView.as_view(), name='alerta_list'),
    
    # Ações
    path('produto/<int:produto_id>/check/', views.check_price, name='check_price'),
    path('produto/<int:produto_id>/notify/<int:contato_id>/', views.send_test_notification, name='send_test_notification'),
    path('check-all-prices/', views.check_all_prices, name='check_all_prices'),
    
    # Autenticação WhatsApp
    path('whatsapp/auth/', views.whatsapp_auth, name='whatsapp_auth'),
    
    # Teste de conexão
    path('test-scraper/', views.test_scraper, name='test_scraper'),
]
