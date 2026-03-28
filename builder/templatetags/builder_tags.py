from django import template
from django.utils.safestring import mark_safe

register = template.Library()

FIELD_ICONS = {
    "string": "fa-solid fa-font",
    "integer": "fa-solid fa-hashtag",
    "float": "fa-solid fa-divide",
    "boolean": "fa-solid fa-toggle-on",
    "date": "fa-regular fa-calendar",
    "datetime": "fa-regular fa-clock",
    "uri": "fa-solid fa-link",
    "enum": "fa-solid fa-list",
    "object": "fa-solid fa-cube",
}


@register.filter
def field_icon(range_type):
    icon_class = FIELD_ICONS.get(range_type, "fa-solid fa-question")
    return mark_safe(f'<i class="{icon_class}"></i>')


@register.filter
def field_icon_class(range_type):
    return FIELD_ICONS.get(range_type, "fa-solid fa-question")


@register.filter
def get_item(dictionary, key):
    if dictionary is None:
        return None
    return dictionary.get(key)
