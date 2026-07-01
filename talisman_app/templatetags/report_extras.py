from django import template

register = template.Library()

@register.filter
def minus(value, arg):
    try:
        return value - arg
    except (TypeError, ValueError):
        return 0