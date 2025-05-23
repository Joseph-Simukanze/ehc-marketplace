from django import template

register = template.Library()

@register.filter(name='multiply')
def multiply(value, arg):
    """
    Multiplies two values in a Django template.
    Usage: {{ value|multiply:arg }}
    """
    try:
        return value * arg
    except (ValueError, TypeError):
        return 0  # Return 0 if multiplication is not possible

@register.filter(name='dict_item')
def dict_item(d, key):
    """
    Safely retrieves a value from a dictionary in templates.
    Usage: {{ my_dict|dict_item:key }}
    """
    if isinstance(d, dict):
        return d.get(key, '')
    return ''

from django import template

register = template.Library()

@register.filter
def floatval(value):
    try:
        return float(value)
    except:
        return 0.0

@register.filter
def multiply(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return ''
from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return ''

from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return ''
from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    try:
        return dictionary.get(key)
    except AttributeError:
        return ''  # in case dictionary is not actually a dict
from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    """Multiplies the value by the argument."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return ''
