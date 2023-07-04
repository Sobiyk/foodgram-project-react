from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _


class HexColorValidator(RegexValidator):
    regex = r'^#([A-Fa-f0-9]){6}$'
    flags = 0


def validate_not_zero(value):
    if value == 0:
        raise ValidationError(
            _("%(value)s не может быть равно нулю"),
            params={"value": value},
        )
