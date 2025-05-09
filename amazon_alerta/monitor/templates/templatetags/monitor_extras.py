from django import template

register = template.Library()

@register.filter
def sub(value, arg):
    """Subtrai o argumento do valor"""
    return value - arg

@register.filter
def abs(value):
    """Retorna o valor absoluto"""
    return abs(value)
