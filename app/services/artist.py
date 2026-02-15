from app.utils.validator import Validator
from app.utils.exceptions import ValidationError


def validate_artist(request_data: dict):
    rules = {
        "name": ["required", "min_length:3", "max_length:50"],
        "dob": ["required", "date"],
        "gender": ["required"],
        "address": ["required", "min_length: 3", "max_length: 255"],
        "first_release_year": ["required", "numeric"],
        "no_of_albums": ["required", "numeric"],
    }

    validator = Validator(request_data, rules)

    if not validator.validate():
        raise ValidationError(validator.errors)

    return True
