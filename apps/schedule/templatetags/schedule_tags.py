from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    if isinstance(dictionary, dict):
        return dictionary.get(key, '')
    return ''

@register.filter
def index(lst, i):
    try:
        return list(lst)[i]
    except:
        return ''
