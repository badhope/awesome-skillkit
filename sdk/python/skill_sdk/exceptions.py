from typing import Any, Dict, Optional


class SkillSDKError(Exception):
    def __init__(self, message: str, status_code: int = 0, response_data: Any = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class SkillNotFoundError(SkillSDKError):
    def __init__(self, message: str = "Skill not found", status_code: int = 404, response_data: Any = None):
        super().__init__(message, status_code, response_data)


class AuthenticationError(SkillSDKError):
    def __init__(self, message: str = "Authentication failed", status_code: int = 401, response_data: Any = None):
        super().__init__(message, status_code, response_data)


class PermissionDeniedError(SkillSDKError):
    def __init__(self, message: str = "Permission denied", status_code: int = 403, response_data: Any = None):
        super().__init__(message, status_code, response_data)


class RateLimitError(SkillSDKError):
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        status_code: int = 429,
        response_data: Any = None,
        retry_after: Optional[int] = None,
    ):
        super().__init__(message, status_code, response_data)
        self.retry_after = retry_after


class ValidationError(SkillSDKError):
    def __init__(self, message: str = "Validation failed", status_code: int = 422, response_data: Any = None):
        super().__init__(message, status_code, response_data)


class APIError(SkillSDKError):
    def __init__(self, message: str = "API error", status_code: int = 500, response_data: Any = None):
        super().__init__(message, status_code, response_data)


class ConnectionError(SkillSDKError):
    def __init__(self, message: str = "Connection failed", status_code: int = 0, response_data: Any = None):
        super().__init__(message, status_code, response_data)


ERROR_MAP: Dict[int, type] = {
    401: AuthenticationError,
    403: PermissionDeniedError,
    404: SkillNotFoundError,
    422: ValidationError,
    429: RateLimitError,
}
