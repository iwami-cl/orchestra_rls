# myapp/templatetags/getattr_extras.py
from django import template

register = template.Library()

@register.filter
def get_field(obj, attr_name):
    # attr_nameの指定がなければ、__str__を返す
    if not attr_name:
        return str(obj)
    return getattr(obj, attr_name)


@register.filter
def get_field_verbose_name(obj, attr_name):
    field = obj._meta.get_field(attr_name)
    return field.verbose_name