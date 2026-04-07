import pytest
import requests
import yaml
import json
import os
import re
from pathlib import Path
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def _expand_env_vars(obj):
    # Regex to match ${ENV_VAR:-default}
    env_re = re.compile(r"\$\{([^}:]+):-([^}]+)}")

    def expand(value):
        if isinstance(value, str):
            def replacer(match):
                env_var, default = match.group(1), match.group(2)
                return os.environ.get(env_var, default)
            return env_re.sub(replacer, value)
        elif isinstance(value, dict):
            return {k: expand(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [expand(v) for v in value]
        else:
            return value
    return expand(obj)

@pytest.fixture(scope="session")
def config():
    cfg_path = Path(__file__).parent / "config.yml"
    if not cfg_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {cfg_path}")
    try:
        with cfg_path.open("r") as f:
            cfg_raw = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise RuntimeError(f"Invalid YAML in config.yml: {e}")
    cfg_expanded = _expand_env_vars(cfg_raw)
    return cfg_expanded

@pytest.fixture
def load_endpoint_test_data():
    def _loader(path):
        json_path = Path(path)
        if not json_path.exists():
            raise FileNotFoundError(f"Test data file not found: {json_path}")
        with json_path.open("r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                raise RuntimeError(f"Invalid JSON in {json_path}: {e}")
        return data
    return _loader

@pytest.fixture
def merged_test_data(config, load_endpoint_test_data):
    def _merge(endpoint_test_data_path=None):
        base = dict(config.get("test_data", {})) if "test_data" in config else {}
        if endpoint_test_data_path:
            override = load_endpoint_test_data(endpoint_test_data_path)
            if not isinstance(override, dict):
                raise ValueError("Endpoint test data must be a dict.")
            base.update(override)
        return base
    return _merge

class APIClient:
    def __init__(self, base_url, timeout=None, retries=3, backoff_factor=0.3):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        retry_strategy = Retry(
            total=retries,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT", "PATCH", "DELETE"],
            backoff_factor=backoff_factor,
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        self.timeout = timeout

    def make_request(self, endpoint, method="GET", headers=None, **kwargs):
        url = self.base_url + "/" + endpoint.lstrip("/")
        req_headers = headers or {}
        timeout = kwargs.pop("timeout", self.timeout)
        resp = self.session.request(method, url, headers=req_headers, timeout=timeout, **kwargs)
        return resp

    def get(self, endpoint, headers=None, **kwargs):
        return self.make_request(endpoint, "GET", headers, **kwargs)

    def post(self, endpoint, headers=None, **kwargs):
        return self.make_request(endpoint, "POST", headers, **kwargs)

    def put(self, endpoint, headers=None, **kwargs):
        return self.make_request(endpoint, "PUT", headers, **kwargs)

    def patch(self, endpoint, headers=None, **kwargs):
        return self.make_request(endpoint, "PATCH", headers, **kwargs)

    def delete(self, endpoint, headers=None, **kwargs):
        return self.make_request(endpoint, "DELETE", headers, **kwargs)

@pytest.fixture
def api_client(config):
    host = config.get("api", {}).get("host", "")
    if not host:
        raise ValueError("'api.host' must be defined in config.yml")
    host = host.strip()
    timeout = config.get("api", {}).get("timeout", None)
    retries = config.get("api", {}).get("retries", 3)
    backoff_factor = config.get("api", {}).get("backoff_factor", 0.3)
    try:
        retries = int(retries)
        backoff_factor = float(backoff_factor)
    except ValueError:
        retries = 3
        backoff_factor = 0.3
    return APIClient(base_url=host, timeout=timeout, retries=retries, backoff_factor=backoff_factor)

@pytest.fixture
def get_config(config):
    def _getter(key, default=None):
        parts = key.split(".")
        val = config
        for part in parts:
            if isinstance(val, dict) and part in val:
                val = val[part]
            else:
                return default
        return val
    return _getter

def pytest_configure(config):
    config.addinivalue_line("markers", "smoke: mark test as smoke test")
