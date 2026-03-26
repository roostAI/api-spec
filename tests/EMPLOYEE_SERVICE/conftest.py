import pytest
import os
import pathlib
import yaml
import json
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import re

# 1) Configuration loading with env var expansion

def _expand_env_vars(data):
    pattern = re.compile(r"\${([^}:s]+):-([^}]+)}")
    if isinstance(data, dict):
        return {k: _expand_env_vars(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [_expand_env_vars(item) for item in data]
    elif isinstance(data, str):
        def replace(match):
            env_var = match.group(1)
            default = match.group(2)
            return os.environ.get(env_var, default)
        return pattern.sub(replace, data)
    else:
        return data

@pytest.fixture(scope="session")
def config():
    config_path = pathlib.Path(__file__).parent / "config.yml"
    if not config_path.exists():
        raise RuntimeError(f"config.yml not found at: {config_path}")
    try:
        with open(config_path, "r") as f:
            raw_cfg = yaml.safe_load(f)
    except Exception as e:
        raise RuntimeError(f"Failed to load config.yml: {e}")
    cfg = _expand_env_vars(raw_cfg)
    return cfg

# 2) Endpoint test data loading and override behavior

@pytest.fixture
def load_endpoint_test_data():
    def _load(path):
        full_path = pathlib.Path(path)
        if not full_path.exists():
            raise RuntimeError(f"Endpoint test data file not found: {path}")
        try:
            with open(full_path, "r") as f:
                return json.load(f)
        except Exception as e:
            raise RuntimeError(f"Failed to load endpoint test data from {path}: {e}")
    return _load

@pytest.fixture
def merged_test_data(config, load_endpoint_test_data):
    def _merge(path):
        cfg_td = config.get("test_data", {})
        endpoint_td = load_endpoint_test_data(path)
        merged = dict(cfg_td)
        merged.update(endpoint_td)
        return merged
    return _merge

# 3) API Client Fixture

class APIClient:
    def __init__(self, base_url, api_key_header=None, api_key_value=None, timeout=10, max_retries=3):
        self.base_url = base_url.strip()
        self.session = requests.Session()
        retries = Retry(total=max_retries, backoff_factor=0.5,
                        status_forcelist=[500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        self.timeout = timeout
        self.api_key_header = api_key_header
        self.api_key_value = api_key_value

    def _prep_headers(self, headers):
        hdrs = headers.copy() if headers else {}
        if self.api_key_header and self.api_key_value:
            hdrs[self.api_key_header] = self.api_key_value
        return hdrs

    def make_request(self, endpoint, method="GET", headers=None, **kwargs):
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        hdrs = self._prep_headers(headers)
        resp = self.session.request(
            method=method,
            url=url,
            headers=hdrs,
            timeout=self.timeout,
            **kwargs
        )
        return resp

    def get(self, endpoint, headers=None, **kwargs):
        return self.make_request(endpoint, method="GET", headers=headers, **kwargs)

    def post(self, endpoint, headers=None, **kwargs):
        return self.make_request(endpoint, method="POST", headers=headers, **kwargs)

    def put(self, endpoint, headers=None, **kwargs):
        return self.make_request(endpoint, method="PUT", headers=headers, **kwargs)

    def patch(self, endpoint, headers=None, **kwargs):
        return self.make_request(endpoint, method="PATCH", headers=headers, **kwargs)

    def delete(self, endpoint, headers=None, **kwargs):
        return self.make_request(endpoint, method="DELETE", headers=headers, **kwargs)

@pytest.fixture
def api_client(config):
    api_cfg = config.get("api", {})
    host = api_cfg.get("host", "").strip()
    if not host:
        raise RuntimeError("api.host missing in config.yml")
    auth_cfg = config.get("auth", {})
    api_key_header = auth_cfg.get("api_key_header") if "api_key_header" in auth_cfg else None
    api_key_value = auth_cfg.get("api_key_value") if "api_key_value" in auth_cfg else None
    timeout = api_cfg.get("timeout", 10)
    retries = api_cfg.get("retries", 3)
    return APIClient(
        base_url=host,
        api_key_header=api_key_header,
        api_key_value=api_key_value,
        timeout=timeout,
        max_retries=retries
    )

# 4) Dynamic Config Getter

def _get_by_dotted(cfg, dotted):
    keys = dotted.split('.')
    val = cfg
    for k in keys:
        if isinstance(val, dict) and k in val:
            val = val[k]
        else:
            raise KeyError(f"Config key '{dotted}' not found")
    return val

@pytest.fixture
def get_config(config):
    def _getter(dotted_key):
        return _get_by_dotted(config, dotted_key)
    return _getter

# 5) Test markers

def pytest_configure(config):
    config.addinivalue_line(
        "markers", "smoke: mark test as smoke"
    )
