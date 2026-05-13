import pytest
import os
import yaml
import json
import re
from pathlib import Path
import requests
from requests.adapters import HTTPAdapter, Retry

CONFIG_YML_FILENAME = "config.yml"
ENV_VAR_PATTERN = re.compile(r"\$\{([^}:]+):-([^}]+)\}")

def _expand_env_vars(value):
    if isinstance(value, str):
        def _replace(match):
            var_name = match.group(1)
            default = match.group(2)
            return os.environ.get(var_name, default)
        return ENV_VAR_PATTERN.sub(_replace, value)
    elif isinstance(value, dict):
        return {k: _expand_env_vars(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [_expand_env_vars(item) for item in value]
    else:
        return value

def _load_config():
    conf_path = Path(__file__).parent / CONFIG_YML_FILENAME
    if not conf_path.is_file():
        raise FileNotFoundError(f"Configuration file '{conf_path}' not found.")
    try:
        with conf_path.open("r", encoding="utf-8") as ymlfile:
            raw_config = yaml.safe_load(ymlfile)
    except Exception as ex:
        raise RuntimeError(f"Failed to parse YAML config at '{conf_path}': {ex}")
    if not isinstance(raw_config, dict):
        raise RuntimeError(f"Config at '{conf_path}' is not a dict.")
    config = _expand_env_vars(raw_config)
    return config

@pytest.fixture(scope="session")
def config():
    return _load_config()

@pytest.fixture
def load_endpoint_test_data():
    def _loader(json_path):
        p = Path(json_path)
        if not p.is_file():
            raise FileNotFoundError(f"Endpoint test data file '{json_path}' not found.")
        try:
            with p.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as ex:
            raise RuntimeError(f"Failed to load endpoint test data: {json_path}: {ex}")
        if not isinstance(data, dict):
            raise RuntimeError(f"Endpoint test data at '{json_path}' must be an object.")
        return data
    return _loader

@pytest.fixture
def merged_test_data(config, load_endpoint_test_data):
    def _merge(json_path=None):
        base = dict(config.get("test_data") or {})
        if json_path:
            override = load_endpoint_test_data(json_path)
            base.update(override)
        return base
    return _merge

class APIClient:
    def __init__(self, base_url, headers=None, timeout=10, max_retries=3, backoff_factor=0.3):
        self.base_url = base_url.strip().rstrip('/')
        self.headers = headers or {}
        self.session = requests.Session()
        retries = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
        )
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        self.timeout = timeout

    def make_request(self, endpoint, method="GET", headers=None, **kwargs):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        merged_headers = self.headers.copy()
        if headers:
            merged_headers.update(headers)
        resp = self.session.request(
            method=method.upper(),
            url=url,
            headers=merged_headers,
            timeout=self.timeout,
            **kwargs
        )
        return resp

    def get(self, endpoint, **kwargs):
        return self.make_request(endpoint, method="GET", **kwargs)

    def post(self, endpoint, **kwargs):
        return self.make_request(endpoint, method="POST", **kwargs)

    def put(self, endpoint, **kwargs):
        return self.make_request(endpoint, method="PUT", **kwargs)

    def patch(self, endpoint, **kwargs):
        return self.make_request(endpoint, method="PATCH", **kwargs)

    def delete(self, endpoint, **kwargs):
        return self.make_request(endpoint, method="DELETE", **kwargs)

@pytest.fixture
def api_client(config):
    host = config.get("api", {}).get("host", "").strip()
    if not host:
        raise ValueError("API host missing in config['api']['host']")
    headers = {}
    auth = config.get("auth", {})
    api_key_header = auth.get("api_key_header")
    api_key_val = auth.get("api_key")
    if api_key_header and api_key_val:
        headers[api_key_header] = api_key_val

    timeout = config.get("api", {}).get("timeout", 10)
    max_retries = config.get("api", {}).get("max_retries", 3)
    backoff_factor = config.get("api", {}).get("backoff_factor", 0.3)
    return APIClient(
        base_url=host,
        headers=headers,
        timeout=timeout,
        max_retries=max_retries,
        backoff_factor=backoff_factor
    )

def _get_by_dotted_key(obj, key):
    keys = key.split(".")
    val = obj
    for k in keys:
        if not isinstance(val, dict) or k not in val:
            raise KeyError(f"Config key '{key}' not found")
        val = val[k]
    return val

@pytest.fixture
def get_config(config):
    def _getter(key):
        return _get_by_dotted_key(config, key)
    return _getter

def pytest_configure(config):
    config.addinivalue_line("markers", "smoke: mark test as smoke test")
