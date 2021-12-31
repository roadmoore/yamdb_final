from django.core.exceptions import ValidationError
from django.utils import timezone


def year_validator(value):
    year = timezone.now().year
    if value >= year:
        raise ValidationError(
            ("%(value)s is not a correcrt year!"),
            params={"value": value},
        )
