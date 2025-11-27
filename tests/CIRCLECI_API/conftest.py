# conftest.py
import os
import re
from pathlib import Path
from typing import Any, Dict, Optional, Union

import pytest
import requests
import yaml
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def _get_config_path() -> Path:
    # Use os.path.join to find the config file in the same directory as this conftest.py
    config_path_str = os.path.join(os.path.dirname(__file__), "config.yml")
    return Path(config_path_str).resolve()


_ENV_PATTERN = re.compile(r"\$\{([A-Za-z0-9_\-]+)(?::-(.*?))?\}")


def _expand_env_in_string(value: str) -> str:
    """
    Expand patterns like ${ENV_VAR:-default} within a string using os.environ.
    Supports hyphens in variable names per provided config structure.
    """
    def replacer(match: re.Match) -> str:
        var = match.group(1)
        default = match.group(2) if match.group(2) is not None else ""
        return os.environ.get(var, default)

    # Replace all occurrences
    result = _ENV_PATTERN.sub(replacer, value)
    return result


def _expand_env(obj: Any) -> Any:
    """
    Recursively expand environment variables in strings within dicts/lists.
    """
    if isinstance(obj, str):
        return _expand_env_in_string(obj)
    elif isinstance(obj, list):
        return [_expand_env(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: _expand_env(v) for k, v in obj.items()}
    else:
        return obj


def _load_yaml_config(config_path: Path) -> Dict[str, Any]:
    """
    Load YAML config with error handling.
    """
    if not config_path.exists():
        raise pytest.UsageError(f"Configuration file not found at: {config_path}")

    try:
        with config_path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        raise pytest.UsageError(f"Error parsing YAML configuration at {config_path}: {e}") from e
    except OSError as e:
        raise pytest.UsageError(f"Error reading configuration at {config_path}: {e}") from e

    # Expand env placeholders like ${VAR:-default}
    data = _expand_env(data)
    return data


class APIClient:
    """
    Simple API client that uses requests.Session with retry and timeout handling.
    Config-driven base URL and authentication.
    """
    def __init__(
        self,
        base_url: str,
        auth: Optional[Dict[str, Any]] = None,
        timeout: Optional[Union[float, tuple]] = None,
        retries: int = 3,
        backoff_factor: float = 0.5,
    ):
        self.base_url = (base_url or "").strip().rstrip("/")
        self.auth = auth or {}

        # Resolve timeout (connect, read) if tuple, else uniform for both
        if timeout is None:
            # Default timeout: connect=10s, read=30s
            self.timeout = (10.0, 30.0)
        else:
            if isinstance(timeout, (int, float)):
                self.timeout = (float(timeout), float(timeout))
            else:
                self.timeout = timeout

        self.session = requests.Session()

        # Configure retries for idempotent requests and also allow other methods
        retry_strategy = Retry(
            total=retries,
            connect=retries,
            read=retries,
            status=retries,
            allowed_methods=False,  # Retry on any method; we'll handle via status_forcelist
            backoff_factor=backoff_factor,
            status_forcelist=(429, 500, 502, 503, 504),
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Default headers and query params derived from auth if present
        self.default_headers: Dict[str, str] = {}
        self.default_query_params: Dict[str, str] = {}

        # Per provided configuration structure:
        # - auth.api_key_header -> Use as header value for "Circle-Token" (if non-empty)
        # - auth.api_key_query -> Use as query param value under key "circle-token" (if non-empty)
        api_key_header_val = (self.auth.get("api_key_header") or "").strip()
        if api_key_header_val:
            self.default_headers["Circle-Token"] = api_key_header_val

        api_key_query_val = (self.auth.get("api_key_query") or "").strip()
        if api_key_query_val:
            self.default_query_params["circle-token"] = api_key_query_val

    def _join_url(self, endpoint: str) -> str:
        endpoint = (endpoint or "").strip()
        if not endpoint:
            return self.base_url
        if endpoint.startswith("http://") or endpoint.startswith("https://"):
            return endpoint
        if endpoint.startswith("/"):
            endpoint = endpoint[1:]
        return f"{self.base_url}/{endpoint}"

    def make_request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        method: str = "GET",
        json: Any = None,
        data: Any = None,
        timeout: Optional[Union[float, tuple]] = None,
    ) -> requests.Response:
        url = self._join_url(endpoint)
        merged_headers = dict(self.default_headers)
        if headers:
            merged_headers.update(headers)

        merged_params = dict(self.default_query_params)
        if params:
            merged_params.update(params)

        response = self.session.request(
            method=method.upper(),
            url=url,
            headers=merged_headers,
            params=merged_params,
            json=json,
            data=data,
            timeout=timeout if timeout is not None else self.timeout,
        )
        return response

    def get(self, endpoint: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None) -> requests.Response:
        return self.make_request(endpoint, params=params, headers=headers, method="GET")

    def post(self, endpoint: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None, json: Any = None, data: Any = None) -> requests.Response:
        return self.make_request(endpoint, params=params, headers=headers, method="POST", json=json, data=data)

    def put(self, endpoint: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None, json: Any = None, data: Any = None) -> requests.Response:
        return self.make_request(endpoint, params=params, headers=headers, method="PUT", json=json, data=data)

    def patch(self, endpoint: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None, json: Any = None, data: Any = None) -> requests.Response:
        return self.make_request(endpoint, params=params, headers=headers, method="PATCH", json=json, data=data)

    def delete(self, endpoint: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None, json: Any = None, data: Any = None) -> requests.Response:
        return self.make_request(endpoint, params=params, headers=headers, method="DELETE", json=json, data=data)

    def head(self, endpoint: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None) -> requests.Response:
        return self.make_request(endpoint, params=params, headers=headers, method="HEAD")

    def options(self, endpoint: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None) -> requests.Response:
        return self.make_request(endpoint, params=params, headers=headers, method="OPTIONS")


@pytest.fixture(scope="session")
def config() -> Dict[str, Any]:
    """
    Load configuration from config.yml located alongside this conftest.py.
    Environment placeholders like ${VAR:-default} are expanded.
    """
    cfg_path = _get_config_path()
    return _load_yaml_config(cfg_path)


@pytest.fixture(scope="session")
def api_host(config: Dict[str, Any]) -> str:
    # Robust base URL handling
    host = (config.get("api", {}).get("host") or "").strip()
    if not host:
        raise pytest.UsageError("Missing required config key: api.host")
    return host.rstrip("/")


@pytest.fixture(scope="session")
def auth(config: Dict[str, Any]) -> Dict[str, Any]:
    return config.get("auth", {}) or {}


@pytest.fixture(scope="session")
def config_test_data(config: Dict[str, Any]) -> Dict[str, Any]:
    return config.get("test_data", {}) or {}


@pytest.fixture(scope="session")
def api_key_header_value(auth: Dict[str, Any]) -> str:
    return (auth.get("api_key_header") or "").strip()


@pytest.fixture(scope="session")
def api_key_query_value(auth: Dict[str, Any]) -> str:
    return (auth.get("api_key_query") or "").strip()


@pytest.fixture(scope="session")
def api_client(api_host: str, auth: Dict[str, Any]) -> APIClient:
    # Set timeout and retries via environment if desired, else defaults
    timeout_env = os.getenv("API_CLIENT_TIMEOUT", "").strip()
    retries_env = os.getenv("API_CLIENT_RETRIES", "").strip()
    backoff_env = os.getenv("API_CLIENT_BACKOFF", "").strip()

    timeout: Optional[Union[float, tuple]]
    if timeout_env:
        try:
            timeout_val = float(timeout_env)
            timeout = (timeout_val, timeout_val)
        except ValueError:
            timeout = None
    else:
        timeout = None

    try:
        retries = int(retries_env) if retries_env else 3
    except ValueError:
        retries = 3

    try:
        backoff = float(backoff_env) if backoff_env else 0.5
    except ValueError:
        backoff = 0.5

    return APIClient(
        base_url=api_host,
        auth=auth,
        timeout=timeout,
        retries=retries,
        backoff_factor=backoff,
    )


def pytest_configure(config: pytest.Config) -> None:
    # Register pytest markers
    config.addinivalue_line("markers", "smoke: For all success scenarios")
