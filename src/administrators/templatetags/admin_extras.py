from django import template
from django.template.defaultfilters import floatformat

register = template.Library()

@register.filter(name='split')
def split(value, arg):
    """Split a string by the given separator"""
    return [x.strip() for x in value.split(arg)]

@register.filter(name='get_item')
def get_item(lst, i):
    """Get an item from a list by index"""
    try:
        return lst[i]
    except:
        return ''

@register.filter
def currency_format(value):
    try:
        return "{:,.2f}".format(float(value))
    except (ValueError, TypeError):
        return value

@register.filter
def multiply(value, arg):
    """Multiply the arg by the value"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def divisibleby(value, arg):
    """Divide value by arg"""
    try:
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0
