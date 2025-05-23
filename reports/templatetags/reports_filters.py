from django import template

register = template.Library()

@register.filter
def divide(value, arg):
    try:
        return value / arg
    except (TypeError, ZeroDivisionError):
        return None

from django import template
import re

register = template.Library()

LATEX_SPECIAL_CHARS = {
    '&': r'\&',
    '%': r'\%',
    '$': r'\$',
    '#': r'\#',
    '_': r'\_',
    '{': r'\{',
    '}': r'\}',
    '~': r'\textasciitilde{}',
    '^': r'\textasciicircum{}',
    '\\': r'\textbackslash{}',
}

@register.filter(name='tex_escape')
def tex_escape(value):
    if not isinstance(value, str):
        value = str(value)
    return re.sub(r'([&%$#_{}~^\\])', lambda m: LATEX_SPECIAL_CHARS[m.group()], value)


# yourapp/templatetags/math_filters.py
from django import template

register = template.Library()

@register.filter
def div(value, arg):
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError):
        return 0
