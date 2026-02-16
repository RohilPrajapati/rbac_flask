from app.utils.validator import Validator
from app.utils.exceptions import ValidationError


def validate_music(request_data: dict):
    rules = {
        "artist_id": ["required", "numeric"],
        "title": ["required"],
        "album_name": ["required"],
        "genre": ["required"],
    }

    validator = Validator(request_data, rules)

    if not validator.validate():
        raise ValidationError(validator.errors)

    return True
