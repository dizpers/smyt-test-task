from django import template

register = template.Library()


@register.simple_tag
def verbose_name(model):
    return model._meta.verbose_name


@register.simple_tag
def class_name(model):
    return model.__class__.__name__