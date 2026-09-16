import phonenumbers
from django.core.exceptions import ValidationError

def normalize_russian_phone(raw_phone):
    try:
        parsed_phone = phonenumbers.parse(raw_phone, "RU")

        if parsed_phone.country_code != 7:
            raise ValidationError("Разрешены только российские номера.")

        if not phonenumbers.is_valid_number(parsed_phone):
            raise ValidationError("Введён некорректный номер телефона.")

        return phonenumbers.format_number(
            parsed_phone,
            phonenumbers.PhoneNumberFormat.E164
        )

    except phonenumbers.NumberParseException:
        raise ValidationError("Не удалось распознать номер телефона.")
