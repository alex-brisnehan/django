# Tags and filters useful for building an Icalendar file.

from django import template

register = template.Library()

@register.filter
def escape(value):
    """Escapes text for Icalendar files.
    
    For details see http://tools.ietf.org/html/rfc5545.html#section-3.3.11
    """
    return unicode(value).replace('\\', r'\\').replace(',', '\\,').replace(';', '\\;').replace('\n', r'\n') 
