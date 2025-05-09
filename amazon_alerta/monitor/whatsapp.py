import pywhatkit
import time
from datetime import datetime, timedelta
from .models import Produto, Contato, Alerta

class WhatsAppNotifier:
    def __init__(self):
        self.wait_time = 30  # Tempo de espera entre mensagens (segundos)
    
    def format_message(self, produto, preco):
        """Formata a mensagem de alerta"""
        return (
            f"🔔 *ALERTA DE PREÇO* 🔔\n\n"
            f"O produto *{produto.nome}* está com preço abaixo do seu alvo!\n\n"
            f"✅ Preço atual: *R$ {preco}*\n"
            f"🎯 Preço alvo: *R$ {produto.preco_alvo}*\n\n"
            f"📌 Link do produto: {produto.url}\n\n"
            f"Este é um alerta automático do sistema de monitoramento de preços."
        )
    
    def send_notification(self, contato, produto, preco):
        """Envia notificação via WhatsApp"""
        try:
            # Formata o número de telefone (remove o + inicial se houver)
            phone_number = contato.telefone
            if phone_number.startswith('+'):
                phone_number = phone_number[1:]
            
            # Formata a mensagem
            message = self.format_message(produto, preco)
            
            # Calcula o horário para envio (1 minuto no futuro)
            now = datetime.now()
            send_time = now + timedelta(minutes=1)
            
            print(f"Preparando para enviar mensagem para {contato.nome} ({phone_number})...")
            print("Na primeira execução, o WhatsApp Web será aberto e você precisará escanear o QR code.")
            print("Aguarde o navegador abrir...")
            
            # Envia a mensagem
            pywhatkit.sendwhatmsg(
                phone_no=f"+{phone_number}",
                message=message,
                time_hour=send_time.hour,
                time_min=send_time.minute,
                wait_time=self.wait_time,
                tab_close=False  # Mantém a aba aberta para verificação
            )
            
            # Registra o alerta no banco de dados
            Alerta.objects.create(
                produto=produto,
                contato=contato,
                preco_no_momento=preco
            )
            
            print(f"Mensagem enviada com sucesso para {contato.nome}!")
            return True
        except Exception as e:
            print(f"Erro ao enviar notificação: {str(e)}")
            return False
    
    def notify_price_drop(self, produto_id):
        """Notifica contatos sobre queda de preço"""
        try:
            produto = Produto.objects.get(id=produto_id, ativo=True)
            
            # Verifica se o preço está abaixo do alvo
            if produto.preco_atual and produto.preco_atual <= produto.preco_alvo:
                contatos = Contato.objects.filter(ativo=True)
                
                for contato in contatos:
                    self.send_notification(contato, produto, produto.preco_atual)
                    # Espera um pouco entre cada envio para evitar bloqueios
                    time.sleep(5)
                
                return True
            return False
        except Produto.DoesNotExist:
            print(f"Produto com ID {produto_id} não encontrado ou inativo")
            return False
        except Exception as e:
            print(f"Erro ao notificar queda de preço: {str(e)}")
            return False
