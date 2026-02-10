from django import template
import html

register = template.Library()

@register.filter
def clean_code(content):
    if content:
        # Convert &nbsp; to regular spaces without affecting structure
        content = html.unescape(content)
        content = content.replace('&nbsp;', ' ').replace('\xa0', ' ')
    return content