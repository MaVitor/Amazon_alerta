import requests
import json
import re
from decimal import Decimal
from django.conf import settings
from django.utils import timezone
from .models import Produto, HistoricoPreco

class AmazonScraper:
    def __init__(self):
        self.api_key = settings.SCRAPER_API_KEY
        self.base_url = "https://api.scraperapi.com"
    
    def extract_price(self, html_content):
        """Extrai o preço do produto da página HTML da Amazon"""
        # Salva o HTML para debug
        with open('amazon_response.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print("Iniciando extração de preço...")
        
        # Padrão 1: Preço com separação de classes whole e fraction
        pattern1 = r'<span class="a-price-whole">([0-9.,]+)</span><span class="a-price-fraction">([0-9]{2})'
        match1 = re.search(pattern1, html_content)
        if match1:
            whole_part = match1.group(1).replace('.', '').replace(',', '')
            fraction_part = match1.group(2)
            price_str = f"{whole_part}.{fraction_part}"
            print(f"Padrão 1 encontrado: {price_str}")
            return Decimal(price_str)
        
        # Padrão 2: Preço com classe a-offscreen
        pattern2 = r'<span class="a-offscreen">R\$\s*([0-9.,]+)</span>'
        match2 = re.search(pattern2, html_content)
        if match2:
            price_str = match2.group(1).replace('.', '').replace(',', '.')
            print(f"Padrão 2 encontrado: {price_str}")
            return Decimal(price_str)
        
        # Padrão 3: Preço com classe a-price-whole sem fraction
        pattern3 = r'<span class="a-price-whole">([0-9.,]+)</span>'
        match3 = re.search(pattern3, html_content)
        if match3:
            price_str = match3.group(1).replace('.', '').replace(',', '.')
            print(f"Padrão 3 encontrado: {price_str}")
            return Decimal(price_str)
        
        # Padrão 4: Preço com data-a-color="price"
        pattern4 = r'data-a-color="price"[^>]*>R\$\s*([0-9.,]+)'
        match4 = re.search(pattern4, html_content)
        if match4:
            price_str = match4.group(1).replace('.', '').replace(',', '.')
            print(f"Padrão 4 encontrado: {price_str}")
            return Decimal(price_str)
        
        # Padrão 5: Preço com span id="priceblock_ourprice"
        pattern5 = r'id="priceblock_ourprice"[^>]*>R\$\s*([0-9.,]+)'
        match5 = re.search(pattern5, html_content)
        if match5:
            price_str = match5.group(1).replace('.', '').replace(',', '.')
            print(f"Padrão 5 encontrado: {price_str}")
            return Decimal(price_str)
        
        # Padrão 6: Preço com classe a-price-symbol + a-price-whole + a-price-fraction
        pattern6 = r'<span class="a-price[^"]*"[^>]*>[^<]*<span class="a-price-symbol">R\$</span><span class="a-price-whole">([0-9.,]+)</span><span class="a-price-fraction">([0-9]{2})</span>'
        match6 = re.search(pattern6, html_content)
        if match6:
            whole_part = match6.group(1).replace('.', '').replace(',', '')
            fraction_part = match6.group(2)
            price_str = f"{whole_part}.{fraction_part}"
            print(f"Padrão 6 encontrado: {price_str}")
            return Decimal(price_str)
        
        # Padrão 7: Preço com formato R$ 999,99
        pattern7 = r'R\$\s*([0-9]+[,.][0-9]{2})'
        match7 = re.search(pattern7, html_content)
        if match7:
            price_str = match7.group(1).replace('.', '').replace(',', '.')
            print(f"Padrão 7 encontrado: {price_str}")
            return Decimal(price_str)
        
        # Padrão 8: Preço com formato 999,99
        pattern8 = r'([0-9]+[,.][0-9]{2})'
        match8 = re.search(pattern8, html_content)
        if match8:
            price_str = match8.group(1).replace('.', '').replace(',', '.')
            print(f"Padrão 8 encontrado: {price_str}")
            return Decimal(price_str)
        
        print("Nenhum padrão de preço encontrado na página.")
        return None
    
    def scrape_product(self, url):
        """Faz a requisição para a ScraperAPI e extrai o preço do produto"""
        # Verifica se é um link encurtado e tenta expandir
        if 'amzn.to' in url or 'a.co' in url:
            try:
                print(f"Detectado link encurtado: {url}")
                print("Tentando expandir o link...")
                
                # Faz uma requisição HEAD para obter o URL real
                session = requests.Session()
                response = session.head(url, allow_redirects=True)
                expanded_url = response.url
                
                if expanded_url and expanded_url != url:
                    print(f"Link expandido: {expanded_url}")
                    url = expanded_url
                else:
                    print("Não foi possível expandir o link. Usando o original.")
            except Exception as e:
                print(f"Erro ao expandir link: {str(e)}")
        
        params = {
            'api_key': self.api_key,
            'url': url,
            'render': 'true',  # Ativa o JavaScript rendering
            'country_code': 'br',  # Define o país como Brasil
            'keep_headers': 'true'  # Mantém os headers para simular um navegador real
        }
        
        try:
            print(f"Fazendo requisição para a URL: {url}")
            response = requests.get(self.base_url, params=params)
            
            if response.status_code == 200:
                print("Requisição bem-sucedida. Extraindo preço...")
                # Salva o HTML para debug (opcional)
                with open('amazon_response.html', 'w', encoding='utf-8') as f:
                    f.write(response.text)
                
                price = self.extract_price(response.text)
                
                if price:
                    print(f"Preço extraído com sucesso: R$ {price}")
                    return price
                else:
                    print("Não foi possível extrair o preço da página.")
                    return None
            else:
                print(f"Erro ao acessar a API: {response.status_code}")
                print(f"Resposta: {response.text}")
                return None
        except Exception as e:
            print(f"Erro durante o scraping: {str(e)}")
            return None
    
    def update_product_price(self, produto_id):
        """Atualiza o preço de um produto específico"""
        try:
            produto = Produto.objects.get(id=produto_id, ativo=True)
            print(f"Atualizando preço do produto: {produto.nome}")
            
            price = self.scrape_product(produto.url)
            
            if price:
                # Atualiza o preço atual do produto
                produto.preco_atual = price
                produto.ultimo_check = timezone.now()
                produto.save()
                
                # Registra no histórico
                HistoricoPreco.objects.create(
                    produto=produto,
                    preco=price
                )
                
                print(f"Preço atualizado com sucesso para R$ {price}")
                return True, price
            
            print("Falha ao atualizar o preço.")
            return False, None
        except Produto.DoesNotExist:
            print(f"Produto com ID {produto_id} não encontrado ou inativo")
            return False, None
        except Exception as e:
            print(f"Erro ao atualizar preço: {str(e)}")
            return False, None
    
    def check_all_products(self):
        """Verifica todos os produtos ativos"""
        produtos = Produto.objects.filter(ativo=True)
        results = []
        
        print(f"Verificando {produtos.count()} produtos ativos...")
        
        for produto in produtos:
            success, price = self.update_product_price(produto.id)
            results.append({
                'produto': produto.nome,
                'success': success,
                'price': price
            })
        
        return results
