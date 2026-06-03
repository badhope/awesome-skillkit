import time
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import httpx

from skill_sdk.exceptions import ERROR_MAP, APIError, ConnectionError, RateLimitError, SkillSDKError
from skill_sdk.types import (
    AnalyticsDashboardDict,
    CategoryDict,
    CompositionDict,
    PaginatedResult,
    SkillDependencyDict,
    SkillDict,
    SkillSearchResultDict,
    SkillUsageTrendDict,
    SkillVersionDict,
    TagDict,
    TokenDict,
    UserDict,
)


class SkillsAPI:
    def __init__(self, client: "SkillClient"):
        self._client = client

    def list(
        self,
        category_slug: Optional[str] = None,
        tag: Optional[str] = None,
        search: Optional[str] = None,
        complexity: Optional[str] = None,
        status: str = "published",
        sort_by: str = "updated_at",
        sort_order: str = "desc",
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedResult:
        params = {}
        if category_slug:
            params["category_slug"] = category_slug
        if tag:
            params["tag"] = tag
        if search:
            params["search"] = search
        if complexity:
            params["complexity"] = complexity
        if status:
            params["status"] = status
        params["sort_by"] = sort_by
        params["sort_order"] = sort_order
        params["page"] = page
        params["page_size"] = page_size

        data = self._client._request("GET", "/skills", params=params)
        items = [SkillDict.from_dict(item) for item in data.get("items", [])]
        return PaginatedResult(
            items=items,
            total=data.get("total", 0),
            page=data.get("page", page),
            page_size=data.get("page_size", page_size),
        )

    def search(
        self,
        q: str,
        limit: int = 10,
        category_id: Optional[str] = None,
    ) -> List[SkillSearchResultDict]:
        params: Dict[str, Any] = {"q": q, "limit": limit}
        if category_id:
            params["category_id"] = category_id
        data = self._client._request("GET", "/skills/search", params=params)
        return [SkillSearchResultDict.from_dict(item) for item in data]

    def get(self, slug: str) -> SkillDict:
        data = self._client._request("GET", f"/skills/{slug}")
        return SkillDict.from_dict(data)

    def create(self, skill_data: Dict[str, Any]) -> SkillDict:
        data = self._client._request("POST", "/skills", json=skill_data)
        return SkillDict.from_dict(data)

    def update(self, slug: str, skill_data: Dict[str, Any]) -> SkillDict:
        data = self._client._request("PUT", f"/skills/{slug}", json=skill_data)
        return SkillDict.from_dict(data)

    def delete(self, slug: str) -> None:
        self._client._request("DELETE", f"/skills/{slug}")

    def get_featured(self, limit: int = 10) -> List[SkillDict]:
        data = self._client._request("GET", "/skills/featured", params={"limit": limit})
        return [SkillDict.from_dict(item) for item in data]

    def get_popular(self, limit: int = 10) -> List[SkillDict]:
        data = self._client._request("GET", "/skills/popular", params={"limit": limit})
        return [SkillDict.from_dict(item) for item in data]

    def get_trending(self, limit: int = 10) -> List[SkillDict]:
        data = self._client._request("GET", "/skills/trending", params={"limit": limit})
        return [SkillDict.from_dict(item) for item in data]

    def get_versions(self, slug: str) -> List[SkillVersionDict]:
        data = self._client._request("GET", f"/skills/{slug}/versions")
        return [SkillVersionDict.from_dict(item) for item in data]

    def create_version(self, slug: str, version_data: Dict[str, Any]) -> SkillVersionDict:
        data = self._client._request("POST", f"/skills/{slug}/versions", json=version_data)
        return SkillVersionDict.from_dict(data)

    def get_dependencies(self, slug: str) -> List[SkillDependencyDict]:
        data = self._client._request("GET", f"/skills/{slug}/dependencies")
        return [SkillDependencyDict.from_dict(item) for item in data]

    def add_dependency(self, slug: str, dependency_data: Dict[str, Any]) -> SkillDependencyDict:
        data = self._client._request("POST", f"/skills/{slug}/dependencies", json=dependency_data)
        return SkillDependencyDict.from_dict(data)

    def remove_dependency(self, slug: str, dep_id: str) -> None:
        self._client._request("DELETE", f"/skills/{slug}/dependencies/{dep_id}")

    def get_similar(self, slug: str, limit: int = 10) -> List[Dict[str, Any]]:
        return self._client._request("GET", f"/skills/{slug}/similar", params={"limit": limit})

    def rate(self, slug: str, rating: int, comment: Optional[str] = None) -> Dict[str, Any]:
        body: Dict[str, Any] = {"rating": rating}
        if comment:
            body["comment"] = comment
        return self._client._request("POST", f"/skills/{slug}/rate", json=body)

    def log_usage(self, slug: str, action: str = "download") -> Dict[str, Any]:
        return self._client._request("POST", f"/skills/{slug}/use", json={"action": action})


class CategoriesAPI:
    def __init__(self, client: "SkillClient"):
        self._client = client

    def list(self, flat: bool = False, parent_id: Optional[str] = None) -> List[CategoryDict]:
        params: Dict[str, Any] = {"flat": flat}
        if parent_id:
            params["parent_id"] = parent_id
        data = self._client._request("GET", "/categories", params=params)
        return [CategoryDict.from_dict(item) for item in data]

    def tree(self) -> List[CategoryDict]:
        data = self._client._request("GET", "/categories/tree")
        return [CategoryDict.from_dict(item) for item in data]

    def get(self, slug: str) -> CategoryDict:
        data = self._client._request("GET", f"/categories/{slug}")
        return CategoryDict.from_dict(data)


class TagsAPI:
    def __init__(self, client: "SkillClient"):
        self._client = client

    def list(
        self,
        search: Optional[str] = None,
        sort_by: str = "usage_count",
        page: int = 1,
        page_size: int = 50,
    ) -> PaginatedResult:
        params: Dict[str, Any] = {"sort_by": sort_by, "page": page, "page_size": page_size}
        if search:
            params["search"] = search
        data = self._client._request("GET", "/tags", params=params)
        items = [TagDict.from_dict(item) for item in data.get("items", [])]
        return PaginatedResult(
            items=items,
            total=data.get("total", 0),
            page=page,
            page_size=page_size,
        )

    def popular(self, limit: int = 20) -> List[TagDict]:
        data = self._client._request("GET", "/tags/popular", params={"limit": limit})
        return [TagDict.from_dict(item) for item in data]


class AuthAPI:
    def __init__(self, client: "SkillClient"):
        self._client = client

    def login(self, username: str, password: str) -> TokenDict:
        data = self._client._request("POST", "/auth/login", json={"username": username, "password": password})
        token = TokenDict.from_dict(data)
        self._client._access_token = token.access_token
        return token

    def register(self, email: str, username: str, password: str, full_name: Optional[str] = None) -> UserDict:
        body: Dict[str, Any] = {"email": email, "username": username, "password": password}
        if full_name:
            body["full_name"] = full_name
        data = self._client._request("POST", "/auth/register", json=body)
        return UserDict.from_dict(data)

    def refresh(self, refresh_token: str) -> TokenDict:
        data = self._client._request("POST", "/auth/refresh", json={"refresh_token": refresh_token})
        token = TokenDict.from_dict(data)
        self._client._access_token = token.access_token
        return token

    def me(self) -> UserDict:
        data = self._client._request("GET", "/auth/me")
        return UserDict.from_dict(data)


class AnalyticsAPI:
    def __init__(self, client: "SkillClient"):
        self._client = client

    def dashboard(self) -> AnalyticsDashboardDict:
        data = self._client._request("GET", "/analytics/dashboard")
        return AnalyticsDashboardDict.from_dict(data)

    def skill_usage(self, days: int = 30) -> List[SkillUsageTrendDict]:
        data = self._client._request("GET", "/analytics/skills/usage", params={"days": days})
        return [SkillUsageTrendDict.from_dict(item) for item in data.get("trend", [])]

    def popular_skills(self, limit: int = 10) -> List[Dict[str, Any]]:
        return self._client._request("GET", "/analytics/skills/popular", params={"limit": limit})


class CompositionsAPI:
    def __init__(self, client: "SkillClient"):
        self._client = client

    def list(self, search: Optional[str] = None, page: int = 1, page_size: int = 20) -> PaginatedResult:
        params: Dict[str, Any] = {"page": page, "page_size": page_size}
        if search:
            params["search"] = search
        data = self._client._request("GET", "/compositions", params=params)
        items = [CompositionDict.from_dict(item) for item in data.get("items", [])]
        return PaginatedResult(
            items=items,
            total=data.get("total", 0),
            page=data.get("page", page),
            page_size=data.get("page_size", page_size),
        )

    def get(self, slug: str) -> CompositionDict:
        data = self._client._request("GET", f"/compositions/{slug}")
        return CompositionDict.from_dict(data)

    def create(self, composition_data: Dict[str, Any]) -> CompositionDict:
        data = self._client._request("POST", "/compositions", json=composition_data)
        return CompositionDict.from_dict(data)


class SkillClient:
    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        api_key: Optional[str] = None,
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ):
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._timeout = timeout
        self._max_retries = max_retries
        self._retry_delay = retry_delay
        self._access_token: Optional[str] = None
        self._client: Optional[httpx.Client] = None

        self.skills = SkillsAPI(self)
        self.categories = CategoriesAPI(self)
        self.tags = TagsAPI(self)
        self.auth = AuthAPI(self)
        self.analytics = AnalyticsAPI(self)
        self.compositions = CompositionsAPI(self)

    @property
    def _http_client(self) -> httpx.Client:
        if self._client is None:
            self._client = httpx.Client(timeout=self._timeout)
        return self._client

    def set_token(self, token: str) -> None:
        self._access_token = token

    def close(self) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None

    def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> Any:
        url = urljoin(f"{self._base_url}/api/v1", path.lstrip("/"))
        if not url.endswith("/") and path.endswith("/"):
            url = url.rstrip("/")
        if path and not path.endswith("/") and not url.endswith("/"):
            url = url.rstrip("/")

        headers: Dict[str, str] = {}
        if self._access_token:
            headers["Authorization"] = f"Bearer {self._access_token}"
        if self._api_key:
            headers["X-API-Key"] = self._api_key

        last_exception: Optional[Exception] = None

        for attempt in range(self._max_retries + 1):
            try:
                response = self._http_client.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json,
                    headers=headers,
                )

                if response.status_code == 204:
                    return None

                if response.status_code < 300:
                    if response.text.strip():
                        return response.json()
                    return None

                error_data = None
                try:
                    error_data = response.json()
                except Exception:
                    error_data = {"detail": response.text}

                error_message = "Unknown error"
                if isinstance(error_data, dict):
                    error_message = error_data.get("detail", str(error_data))
                elif isinstance(error_data, str):
                    error_message = error_data

                if response.status_code == 429:
                    retry_after = response.headers.get("Retry-After")
                    raise RateLimitError(
                        message=error_message,
                        status_code=response.status_code,
                        response_data=error_data,
                        retry_after=int(retry_after) if retry_after else None,
                    )

                exc_class = ERROR_MAP.get(response.status_code, APIError)
                raise exc_class(
                    message=error_message,
                    status_code=response.status_code,
                    response_data=error_data,
                )

            except (httpx.ConnectError, httpx.TimeoutException, httpx.ConnectTimeout) as e:
                last_exception = ConnectionError(
                    message=f"Connection failed: {str(e)}",
                    status_code=0,
                )
                if attempt < self._max_retries:
                    time.sleep(self._retry_delay * (2 ** attempt))
                    continue
                raise last_exception

            except SkillSDKError:
                raise

            except Exception as e:
                raise APIError(message=f"Unexpected error: {str(e)}", status_code=0)

        if last_exception:
            raise last_exception
        raise APIError(message="Request failed after retries", status_code=0)

    def __enter__(self) -> "SkillClient":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
