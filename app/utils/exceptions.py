class ValidationError(Exception):
    def __init__(self, errors: dict):
        self.errors = errors
        super().__init__("Validation failed")
