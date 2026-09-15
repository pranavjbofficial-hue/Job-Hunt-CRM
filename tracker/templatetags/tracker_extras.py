from django import template

register = template.Library()


@register.filter
def status_badge_class(status):
    return f'badge-status-{status}'
