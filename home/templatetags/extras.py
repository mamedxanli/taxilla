from django import template
from config.local_secrets import GOOGLE_MAPS_API_KEY

register = template.Library()

@register.filter
def addcss(field, css):
    """
    adds css to fields in templates
    """
    return field.as_widget(attrs={"class":css})

@register.simple_tag
def google_api():
    """
    Returns Google api key
    """
    return GOOGLE_MAPS_API_KEY
