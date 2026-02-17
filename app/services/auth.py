from app.utils.validator import Validator
from app.utils.exceptions import ValidationError

REGISTRATION_RULES = {
    "first_name": ["required", "min_length:3", "max_length:50"],
    "last_name": ["required", "min_length:3", "max_length:50"],
    "email": ["required", "email", "max_length:100"],
    "password": ["required", "min_length:8", "max_length:50"],
    "c_password": ["required", "min_length:8", "max_length:50", "match:password"],
    "phone": ["required", "numeric", "min_length:10", "max_length:15"],
    "dob": ["required", "date"],
    "gender": ["required"],
    "address": ["required", "min_length:3", "max_length:255"],
    "role": ["required"],
}


def validate_registration_field(field: str, value, existing_data: dict):
    if field not in REGISTRATION_RULES:
        raise ValidationError({field: f"Unknown field: '{field}'"})

    data = existing_data.copy()
    data[field] = value

    rules = {field: REGISTRATION_RULES[field]}

    validator = Validator(data, rules)

    if not validator.validate():
        raise ValidationError(validator.errors)


def validate_registration(request_data: dict):
    validator = Validator(request_data, REGISTRATION_RULES)

    if not validator.validate():
        raise ValidationError(validator.errors)

    return True


def validate_user_update(request_data: dict):
    rules = {
        "first_name": ["required", "min_length:3", "max_length:50"],
        "last_name": ["required", "min_length:3", "max_length:50"],
        "email": ["required", "email", "max_length:100"],
        "phone": ["required", "numeric", "min_length:10", "max_length:15"],
        "dob": ["required", "date"],
        "gender": ["required"],
        "address": ["required", "min_length: 3", "max_length: 255"],
        "role": ["required"],
    }

    validator = Validator(request_data, rules)

    if not validator.validate():
        raise ValidationError(validator.errors)

    return True


def validate_login(request_data: dict):
    rules = {
        "email": ["required", "email"],
        "password": ["required"],
    }

    validator = Validator(request_data, rules)

    if not validator.validate():
        raise ValidationError(validator.errors)

    return True
