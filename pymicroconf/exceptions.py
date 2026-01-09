class ConfigPropertyRequiredException(Exception):
    """
    ConfigPropertyRequiredException: Raised when a required field is not set
    """

    def __init__(self, field_name: str):
        self.field_name = field_name
        super().__init__(f"Required value for field '{field_name}' is not set")


class InvalidConfigException(Exception):
    """
    InvalidConfigException: Raised when configuration validation fails
    """

    def __init__(self, missing_fields: list[str]):
        self.missing_fields = missing_fields
        super().__init__(f"Missing required fields: {', '.join(missing_fields)}")
