from django.core.management.base import BaseCommand
from monitor.scraper import AmazonScraper
from monitor.whatsapp import WhatsAppNotifier
from monitor.models import Produto

class Command(BaseCommand):
    help = 'Verifica os preços dos produtos e envia notificações se necessário'
    
    def handle(self, *args, **options):
        self.stdout.write('Iniciando verificação de preços...')
        
        # Inicializa o scraper
        scraper = AmazonScraper()
        
        # Inicializa o notificador
        notifier = WhatsAppNotifier()
        
        # Verifica todos os produtos
        results = scraper.check_all_products()
        
        # Conta os produtos verificados com sucesso
        success_count = sum(1 for result in results if result['success'])
        
        self.stdout.write(f'Verificados {len(results)} produtos, {success_count} com sucesso.')
        
        # Verifica produtos com preço abaixo do alvo
        produtos = Produto.objects.filter(ativo=True, preco_atual__isnull=False)
        for produto in produtos:
            if produto.preco_atual <= produto.preco_alvo:
                self.stdout.write(f'Produto {produto.nome} está com preço abaixo do alvo! Enviando notificações...')
                notifier.notify_price_drop(produto.id)
        
        self.stdout.write('Verificação concluída!')
