from django import template

register = template.Library()


@register.filter
def format_phone(phone):
    if not phone:
        return ''

    digits = ''.join(filter(str.isdigit, phone))

    if len(digits) != 11 or not digits.startswith('7'):
        return phone

    return (
        f'+7 ({digits[1:4]}) '
        f'{digits[4:7]}-{digits[7:9]}-{digits[9:11]}'
    )
