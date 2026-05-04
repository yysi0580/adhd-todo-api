class AppError(Exception):
    code = "APP_ERROR"
    status_code = 400

    def __init__(self, message: str, code: str | None = None, status_code: int | None = None):
        self.message = message
        self.code = code or self.code
        self.status_code = status_code or self.status_code
        super().__init__(message)


class NotFoundError(AppError):
    code = "NOT_FOUND"
    status_code = 404


class PermissionDeniedError(AppError):
    code = "PERMISSION_DENIED"
    status_code = 403


class InvalidStateTransitionError(AppError):
    code = "INVALID_STATE_TRANSITION"
    status_code = 400


class DuplicateActionError(AppError):
    code = "DUPLICATE_ACTION"
    status_code = 409


class ValidationDomainError(AppError):
    code = "VALIDATION_ERROR"
    status_code = 400


def not_found(message: str, code: str = "NOT_FOUND") -> AppError:
    return NotFoundError(message=message, code=code)


def bad_request(message: str, code: str = "VALIDATION_ERROR") -> AppError:
    return ValidationDomainError(message=message, code=code)
