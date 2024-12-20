from django import template

register = template.Library()

@register.filter(name='addclass')
def addclass(field, css):
    return field.as_widget(attrs={'class': css})

@register.filter(name='attr')
def attr(field, attr_args):
    attr, value = attr_args.split(':')
    return field.as_widget(attrs={attr: value})
