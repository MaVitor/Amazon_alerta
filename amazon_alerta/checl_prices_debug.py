import os
import django
import time
import requests
import re
from decimal import Decimal

# Configurar o ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'amazon_alerta.settings')
django.setup()

# Importar após configurar o ambiente
from django.conf import settings

def expand_short_url(url):
    """Expande um URL encurtado para o URL completo"""
    try:
        print(f"Tentando expandir URL: {url}")
        session = requests.Session()
        response = session.head(url, allow_redirects=True)
        expanded_url = response.url
        print(f"URL expandido: {expanded_url}")
        return expanded_url
    except Exception as e:
        print(f"Erro ao expandir URL: {str(e)}")
        return url

def extract_price_debug(html_content):
    """Versão de depuração para extrair o preço"""
    # Salva o HTML para análise
    with open('amazon_debug.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("\nBuscando padrões de preço no HTML...")
    
    # Lista de padrões para testar
    patterns = [
        # Padrão 1: Preço com separação de classes whole e fraction
        r'<span class="a-price-whole">([0-9.,]+)</span><span class="a-price-fraction">([0-9]{2})',
        
        # Padrão 2: Preço com classe a-offscreen
        r'<span class="a-offscreen">R\$\s*([0-9.,]+)</span>',
        
        # Padrão 3: Preço com classe a-price-whole sem fraction
        r'<span class="a-price-whole">([0-9.,]+)</span>',
        
        # Padrão 4: Preço com data-a-color="price"
        r'data-a-color="price"[^>]*>R\$\s*([0-9.,]+)',
        
        # Padrão 5: Preço com span id="priceblock_ourprice"
        r'id="priceblock_ourprice"[^>]*>R\$\s*([0-9.,]+)',
        
        # Padrão 6: Preço com classe a-price-symbol + a-price-whole + a-price-fraction
        r'<span class="a-price[^"]*"[^>]*>[^<]*<span class="a-price-symbol">R\$</span><span class="a-price-whole">([0-9.,]+)</span><span class="a-price-fraction">([0-9]{2})</span>',
        
        # Padrão 7: Preço com formato R$ 999,99
        r'R\$\s*([0-9]+[,.][0-9]{2})',
        
        # Padrão 8: Preço com formato 999,99
        r'([0-9]+[,.][0-9]{2})'
    ]
    
    # Testa cada padrão
    for i, pattern in enumerate(patterns, 1):
        matches = re.findall(pattern, html_content)
        print(f"\nTestando Padrão {i}:")
        if matches:
            print(f"Encontradas {len(matches)} correspondências:")
            for j, match in enumerate(matches[:5], 1):  # Mostra até 5 correspondências
                if isinstance(match, tuple):
                    if len(match) == 2:  # Padrão com whole e fraction
                        whole_part = match[0].replace('.', '').replace(',', '')
                        fraction_part = match[1]
                        price_str = f"{whole_part}.{fraction_part}"
                        print(f"  Match {j}: {price_str}")
                    else:
                        print(f"  Match {j}: {match}")
                else:
                    price_str = match.replace('.', '').replace(',', '.')
                    print(f"  Match {j}: {price_str}")
            
            if len(matches) > 5:
                print(f"  ... e mais {len(matches) - 5} correspondências")
        else:
            print("  Nenhuma correspondência encontrada")
    
    print("\nAnálise de preço concluída. Verifique o arquivo 'amazon_debug.html' para mais detalhes.")

def test_scraper_api():
    """Testa a conexão com a ScraperAPI e a extração de preços"""
    if not hasattr(settings, 'SCRAPER_API_KEY') or not settings.SCRAPER_API_KEY:
        print("ERRO: A chave da API ScraperAPI não está configurada!")
        return
    
    print(f"Usando a chave da API: {settings.SCRAPER_API_KEY[:5]}...")
    
    # Solicita a URL do produto
    url = input("Digite a URL do produto da Amazon (ou pressione Enter para usar uma URL de exemplo): ")
    if not url:
        url = "https://www.amazon.com.br/dp/B0BZ418DCW"  # URL de exemplo
    
    # Se for um link encurtado, tenta expandir
    if 'amzn.to' in url or 'a.co' in url:
        url = expand_short_url(url)
    
    # Parâmetros para a ScraperAPI
    params = {
        'api_key': settings.SCRAPER_API_KEY,
        'url': url,
        'render': 'true',  # Ativa o JavaScript rendering
        'country_code': 'br',  # Define o país como Brasil
        'keep_headers': 'true'  # Mantém os headers para simular um navegador real
    }
    
    try:
        print(f"Fazendo requisição para a URL: {url}")
        response = requests.get("https://api.scraperapi.com", params=params)
        
        if response.status_code == 200:
            print("Requisição bem-sucedida!")
            
            # Analisa o HTML para encontrar padrões de preço
            extract_price_debug(response.text)
        else:
            print(f"Erro ao acessar a API: {response.status_code}")
            print(f"Resposta: {response.text[:500]}...")  # Primeiros 500 caracteres
    except Exception as e:
        print(f"Erro durante o teste: {str(e)}")

if __name__ == '__main__':
    print("=== Ferramenta de Depuração do ScraperAPI ===")
    test_scraper_api()
