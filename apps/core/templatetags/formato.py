from django import template

register = template.Library()


@register.filter(name='precio_cop')
def precio_cop(valor):
    """
    Convierte un número (45000) en formato de pesos colombianos (45.000).
    """
    try:
        numero = int(float(valor))
        return f"{numero:,}".replace(',', '.')
    except (ValueError, TypeError):
        return valor