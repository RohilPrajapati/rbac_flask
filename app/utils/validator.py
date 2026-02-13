import re
from datetime import datetime



class Validator:
    def __init__(self, data, rules):
        self.data = data
        self.rules = rules
        self.errors = {}

    def validate(self):
        for field, rule_list in self.rules.items():
            value = self.data.get(field, "").strip()

            for rule in rule_list:
                if rule == "required":
                    if not value:
                        self.add_error(
                            field, f"{field.replace('_', ' ').title()} is required."
                        )

                elif rule.startswith("min_length:"):
                    length = int(rule.split(":")[1])
                    if value and len(value) < length:
                        self.add_error(
                            field,
                            f"{field.title()} must be at least {length} characters.",
                        )

                elif rule.startswith("max_length:"):
                    length = int(rule.split(":")[1])
                    if value and len(value) > length:
                        self.add_error(
                            field,
                            f"{field.replace('_', ' ').title()} must not exceed {length} characters.",
                        )

                elif rule == "email":
                    pattern = r"^[^@]+@[^@]+\.[^@]+$"
                    if value and not re.match(pattern, value):
                        self.add_error(field, "Invalid email address.")

                elif rule.startswith("match:"):
                    other_field = rule.split(":")[1]
                    if value != self.data.get(other_field, ""):
                        self.add_error(
                            field, f"{field.title()} does not match {other_field}."
                        )

                elif rule == "numeric":
                    if value and not value.isdigit():
                        self.add_error(field, f"{field.title()} must be numeric.")

                elif rule == "date":
                    try:
                        if value:
                            datetime.strptime(value, "%Y-%m-%d")
                    except ValueError:
                        self.add_error(field, "Invalid date format (YYYY-MM-DD).")

                elif rule.startswith("in:"):
                    allowed = rule.split(":")[1].split(",")
                    if value not in allowed:
                        self.add_error(field, f"Invalid {field} selected.")

        return len(self.errors) == 0

    def add_error(self, field, message):
        if field not in self.errors:
            self.errors[field] = message
