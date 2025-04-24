"""Define Custom Exceptions for the application."""


class CreateCheckoutSessionError(Exception):
    """Exception raised when failing to create a checkout session."""

    def __init__(self, message: str) -> None:
        """Initialize the exception with a message."""
        super().__init__(message)
        self.message = message
