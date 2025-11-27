# conftest.py

import os
import re
from typing import Any, Dict, Optional, Tuple, Union
from pathlib import Path
from urllib.parse import urljoin

import pytest
import requests
import yaml
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


_ENV_VAR_PATTERN = re.compile(r"\$\{([^}:]+)(?::-(.*?)?)?\}")


def _expand_env_in_string(value: str) -> str:
    """
    Expand environment variables in the form:
      - ${VAR}
      - ${VAR:-default}
    """
    def repl(match: re.Match) -> str:
        var_name = match.group(1)
        default_val = match.group(2) if match.group(2) is not None else ""
        return os.environ.get(var_name, default_val)

    # Replace repeatedly until stable, in case resulting defaults contain patterns too.
    previous = None
    current = value
    # Prevent infinite loop; limit iterations
    for _ in range(5):
        if current == previous:
            break
        previous = current
        current = _ENV_VAR_PATTERN.sub(repl, current)
    return current


def _expand_env(obj: Any) -> Any:
    """
    Recursively expand env variables for dict/list/str structures.
    """
    if isinstance(obj, dict):
        return {k: _expand_env(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_expand_env(i) for i in obj]
    if isinstance(obj, str):
        return _expand_env_in_string(obj)
    return obj


def _load_yaml_config() -> Dict[str, Any]:
    """
    Load config.yml from the same directory as this file with error handling.
    """
    here = Path(__file__).parent.resolve()
    # Use os.path.join as requested
    config_path = os.path.join(str(here), "config.yml")

    if not os.path.exists(config_path):
        raise pytest.UsageError(
            f"config.yml not found at path: {config_path}. Ensure the file exists alongside conftest.py."
        )

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        raise pytest.UsageError(f"Failed to parse YAML at {config_path}: {e}") from e
    except OSError as e:
        raise pytest.UsageError(f"Unable to read config file at {config_path}: {e}") from e

    # Expand environment variables like ${VAR} and ${VAR:-default}
    expanded = _expand_env(raw)
    if not isinstance(expanded, dict):
        raise pytest.UsageError("Top-level YAML structure must be a mapping (dict).")

    return expanded


class APIClient:
    """
    Simple API client using requests.Session with retries and timeouts.
    """

    def __init__(
        self,
        base_url: str,
        default_headers: Optional[Dict[str, str]] = None,
        default_params: Optional[Dict[str, str]] = None,
        timeout: Tuple[Union[int, float], Union[int, float]] = (10, 30),
        retries: int = 3,
        backoff_factor: float = 0.5,
    ) -> None:
        self.base_url = (base_url or "").strip()
        self.default_headers = default_headers or {}
        self.default_params = default_params or {}
        self.default_timeout = timeout

        self.session = requests.Session()
        retry = Retry(
            total=retries,
            connect=retries,
            read=retries,
            backoff_factor=backoff_factor,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset(["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"]),
            raise_on_status=False,
            respect_retry_after_header=True,
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        # A simple default UA to help trace
        self.session.headers.update({"User-Agent": "pytest-api-client/1.0"})

    def _build_url(self, endpoint: str) -> str:
        endpoint = endpoint.strip() if isinstance(endpoint, str) else ""
        # urljoin handles leading/trailing slashes robustly
        return urljoin(self.base_url.rstrip("/") + "/", endpoint.lstrip("/"))

    def make_request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        method: str = "GET",
        json: Any = None,
        data: Any = None,
        timeout: Optional[Tuple[Union[int, float], Union[int, float]]] = None,
    ) -> requests.Response:
        url = self._build_url(endpoint)
        req_headers = dict(self.default_headers)
        if headers:
            req_headers.update(headers)

        req_params = dict(self.default_params)
        if params:
            req_params.update(params)

        used_timeout = timeout if timeout is not None else self.default_timeout

        response = self.session.request(
            method=method.upper(),
            url=url,
            headers=req_headers,
            params=req_params,
            json=json,
            data=data,
            timeout=used_timeout,
        )
        return response

    # Convenience methods
    def get(self, endpoint: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None, timeout=None) -> requests.Response:
        return self.make_request(endpoint, params=params, headers=headers, method="GET", timeout=timeout)

    def post(self, endpoint: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None, json: Any = None, data: Any = None, timeout=None) -> requests.Response:
        return self.make_request(endpoint, params=params, headers=headers, method="POST", json=json, data=data, timeout=timeout)

    def put(self, endpoint: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None, json: Any = None, data: Any = None, timeout=None) -> requests.Response:
        return self.make_request(endpoint, params=params, headers=headers, method="PUT", json=json, data=data, timeout=timeout)

    def patch(self, endpoint: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None, json: Any = None, data: Any = None, timeout=None) -> requests.Response:
        return self.make_request(endpoint, params=params, headers=headers, method="PATCH", json=json, data=data, timeout=timeout)

    def delete(self, endpoint: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None, timeout=None) -> requests.Response:
        return self.make_request(endpoint, params=params, headers=headers, method="DELETE", timeout=timeout)

    def head(self, endpoint: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None, timeout=None) -> requests.Response:
        return self.make_request(endpoint, params=params, headers=headers, method="HEAD", timeout=timeout)

    def options(self, endpoint: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None, timeout=None) -> requests.Response:
        return self.make_request(endpoint, params=params, headers=headers, method="OPTIONS", timeout=timeout)


def pytest_configure(config: pytest.Config) -> None:
    # Register markers used in tests
    config.addinivalue_line("markers", "smoke: Mark a test as a smoke (success) scenario")


@pytest.fixture(scope="session")
def config() -> Dict[str, Any]:
    """
    Loaded and environment-expanded configuration from config.yml.
    """
    return _load_yaml_config()


@pytest.fixture(scope="session")
def config_api(config: Dict[str, Any]) -> Dict[str, Any]:
    return dict(config.get("api") or {})


@pytest.fixture(scope="session")
def config_auth(config: Dict[str, Any]) -> Dict[str, Any]:
    return dict(config.get("auth") or {})


@pytest.fixture(scope="session")
def config_test_data(config: Dict[str, Any]) -> Dict[str, Any]:
    return dict(config.get("test_data") or {})


@pytest.fixture(scope="session")
def api_host(config_api: Dict[str, Any]) -> str:
    return (config_api.get("host") or "").strip()


@pytest.fixture(scope="session")
def auth_api_key_header(config_auth: Dict[str, Any]) -> str:
    # Value expected to come from env via ${Circle-Token:-}
    return config_auth.get("api_key_header") or ""


@pytest.fixture(scope="session")
def auth_api_key_query(config_auth: Dict[str, Any]) -> str:
    # Value expected to come from env via ${circle-token:-}
    return config_auth.get("api_key_query") or ""


@pytest.fixture(scope="session")
def api_client(api_host: str) -> APIClient:
    # Create API client using host from config. Timeout/retry are set to sensible defaults.
    return APIClient(
        base_url=api_host,
        default_headers={},
        default_params={},
        timeout=(10, 30),
        retries=3,
        backoff_factor=0.5,
    )
