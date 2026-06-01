export class SkillLibraryError extends Error {
  public statusCode: number;
  public responseData: unknown;

  constructor(message: string, statusCode: number = 0, responseData: unknown = null) {
    super(message);
    this.name = "SkillLibraryError";
    this.statusCode = statusCode;
    this.responseData = responseData;
  }
}

export class SkillNotFoundError extends SkillLibraryError {
  constructor(message: string = "Skill not found", statusCode: number = 404, responseData: unknown = null) {
    super(message, statusCode, responseData);
    this.name = "SkillNotFoundError";
  }
}

export class AuthenticationError extends SkillLibraryError {
  constructor(message: string = "Authentication failed", statusCode: number = 401, responseData: unknown = null) {
    super(message, statusCode, responseData);
    this.name = "AuthenticationError";
  }
}

export class PermissionDeniedError extends SkillLibraryError {
  constructor(message: string = "Permission denied", statusCode: number = 403, responseData: unknown = null) {
    super(message, statusCode, responseData);
    this.name = "PermissionDeniedError";
  }
}

export class RateLimitError extends SkillLibraryError {
  public retryAfter: number | null;

  constructor(
    message: string = "Rate limit exceeded",
    statusCode: number = 429,
    responseData: unknown = null,
    retryAfter: number | null = null,
  ) {
    super(message, statusCode, responseData);
    this.name = "RateLimitError";
    this.retryAfter = retryAfter;
  }
}

export class ValidationError extends SkillLibraryError {
  constructor(message: string = "Validation failed", statusCode: number = 422, responseData: unknown = null) {
    super(message, statusCode, responseData);
    this.name = "ValidationError";
  }
}

export class APIError extends SkillLibraryError {
  constructor(message: string = "API error", statusCode: number = 500, responseData: unknown = null) {
    super(message, statusCode, responseData);
    this.name = "APIError";
  }
}

export class ConnectionError extends SkillLibraryError {
  constructor(message: string = "Connection failed", statusCode: number = 0, responseData: unknown = null) {
    super(message, statusCode, responseData);
    this.name = "ConnectionError";
  }
}

const ERROR_MAP: Record<number, typeof SkillLibraryError> = {
  401: AuthenticationError,
  403: PermissionDeniedError,
  404: SkillNotFoundError,
  422: ValidationError,
  429: RateLimitError,
};

export function createErrorFromStatus(
  statusCode: number,
  message: string,
  responseData: unknown,
  retryAfter?: number | null,
): SkillLibraryError {
  const ErrorClass = ERROR_MAP[statusCode] || APIError;
  if (statusCode === 429) {
    return new RateLimitError(message, statusCode, responseData, retryAfter);
  }
  return new ErrorClass(message, statusCode, responseData);
}