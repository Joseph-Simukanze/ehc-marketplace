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
