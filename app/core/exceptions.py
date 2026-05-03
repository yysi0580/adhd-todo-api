from dataclasses import dataclass


@dataclass
class AppError(Exception):
    message: str
    status_code: int = 400


def not_found(message: str) -> AppError:
    return AppError(message=message, status_code=404)


def bad_request(message: str) -> AppError:
    return AppError(message=message, status_code=400)
