import os
import django
import time

# Configurar o ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'amazon_alerta.settings')
django.setup()

# Importar após configurar o ambiente
from monitor.scraper import AmazonScraper
from monitor.whatsapp import WhatsAppNotifier
from monitor.models import Produto
from django.conf import settings

def check_prices():
    print('Iniciando verificação de preços...')
    
    # Verifica se a chave da API está configurada
    if not hasattr(settings, 'SCRAPER_API_KEY') or not settings.SCRAPER_API_KEY:
        print("ERRO: A chave da API ScraperAPI não está configurada!")
        print("Por favor, adicione sua chave no arquivo .env ou settings.py")
        return
    
    print(f"Usando a chave da API: {settings.SCRAPER_API_KEY[:5]}...")
    
    # Inicializa o scraper
    scraper = AmazonScraper()
    
    # Verifica todos os produtos
    results = scraper.check_all_products()
    
    # Conta os produtos verificados com sucesso
    success_count = sum(1 for result in results if result['success'])
    
    print(f'Verificados {len(results)} produtos, {success_count} com sucesso.')
    
    if success_count > 0:
        # Inicializa o notificador
        notifier = WhatsAppNotifier()
        
        # Verifica produtos com preço abaixo do alvo
        produtos = Produto.objects.filter(ativo=True, preco_atual__isnull=False)
        for produto in produtos:
            if produto.preco_atual <= produto.preco_alvo:
                print(f'Produto {produto.nome} está com preço abaixo do alvo! Enviando notificações...')
                notifier.notify_price_drop(produto.id)
    else:
        print("Nenhum produto foi atualizado com sucesso. Não serão enviadas notificações.")
    
    print('Verificação concluída!')

if __name__ == '__main__':
    check_prices()
