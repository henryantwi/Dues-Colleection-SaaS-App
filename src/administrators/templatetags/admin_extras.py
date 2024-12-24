from django import template

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
