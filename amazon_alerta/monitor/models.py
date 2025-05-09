from django.db import models
from django.utils import timezone

class Produto(models.Model):
    nome = models.CharField(max_length=255)
    url = models.URLField(max_length=500)
    preco_atual = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    preco_alvo = models.DecimalField(max_digits=10, decimal_places=2)
    ultimo_check = models.DateTimeField(null=True, blank=True)
    ativo = models.BooleanField(default=True)
    
    def __str__(self):
        return self.nome
    
    class Meta:
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'

class HistoricoPreco(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='historico')
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    data = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.produto.nome} - R${self.preco} em {self.data.strftime('%d/%m/%Y %H:%M')}"
    
    class Meta:
        verbose_name = 'Histórico de Preço'
        verbose_name_plural = 'Históricos de Preços'
        ordering = ['-data']

class Contato(models.Model):
    nome = models.CharField(max_length=100)
    telefone = models.CharField(max_length=20)  # Formato: +5511999999999
    ativo = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.nome} ({self.telefone})"
    
    class Meta:
        verbose_name = 'Contato'
        verbose_name_plural = 'Contatos'

class Alerta(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    contato = models.ForeignKey(Contato, on_delete=models.CASCADE)
    data_envio = models.DateTimeField(auto_now_add=True)
    preco_no_momento = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"Alerta para {self.contato.nome} sobre {self.produto.nome}"
    
    class Meta:
        verbose_name = 'Alerta'
        verbose_name_plural = 'Alertas'
