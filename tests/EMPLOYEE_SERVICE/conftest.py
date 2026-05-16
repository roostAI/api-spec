import pytest
import requests
import yaml
import json
import os
import re
from pathlib import Path
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

CONFIG_YML_PATH = Path(__file__).parent / "config.yml"

def _expand_env_vars(d):
    """
    Recursively expand environment variable patterns like ${VAR:-default} in values.
    """
    env_pattern = re.compile(r"\$\{([^}:]+):-([^}]+)\}")

    def expand(value):
        if isinstance(value, str):
            def replacer(match):
                var = match.group(1)
                default = match.group(2)
                return os.environ.get(var, default)
            return env_pattern.sub(replacer, value)
        elif isinstance(value, dict):
            return {k: expand(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [expand(v) for v in value]
        else:
            return value

    return expand(d)

@pytest.fixture(scope="session")
def config():
    # Load config.yml
    if not CONFIG_YML_PATH.is_file():
        raise RuntimeError(f"Missing config.yml at {CONFIG_YML_PATH}")
    with open(CONFIG_YML_PATH, "r") as f:
        try:
            cfg = yaml.safe_load(f)
        except Exception as e:
            raise RuntimeError(f"Invalid YAML in config.yml: {e}")
    cfg = _expand_env_vars(cfg)
    return cfg

@pytest.fixture
def load_endpoint_test_data():
    """
    Returns a function to load endpoint test data from JSON file path.
    """
    def _loader(path):
        json_path = Path(path)
        if not json_path.is_file():
            raise RuntimeError(f"Test data JSON file missing at {json_path}")
        with open(json_path, "r") as f:
            try:
                data = json.load(f)
            except Exception as e:
                raise RuntimeError(f"Invalid JSON in endpoint test data: {e}")
        return data
    return _loader

@pytest.fixture
def merged_test_data(config, load_endpoint_test_data):
    """
    Returns a function to merge config['test_data'] and endpoint test data, endpoint values override config.
    """
    def _merger(endpoint_json_path):
        endpoint_data = load_endpoint_test_data(endpoint_json_path)
        base_data = config.get("test_data", {})
        merged = base_data.copy()
        merged.update(endpoint_data)  # endpoint overrides
        return merged
    return _merger

class APIClient:
    def __init__(self, config):
        self.base_url = str(config["api"]["host"]).strip()
        self.session = requests.Session()
        retries = Retry(
            total=3,
            backoff_factor=0.3,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "PUT", "POST", "PATCH", "DELETE", "OPTIONS"]
        )
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        self.timeout = float(config.get("api", {}).get("timeout", 10))

    def make_request(self, endpoint, method="GET", headers=None, **kwargs):
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        resp = self.session.request(
            method=method,
            url=url,
            headers=headers,
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
    return APIClient(config)

@pytest.fixture
def get_config(config):
    """
    Returns a function to fetch config values by dotted key, e.g. 'api.host'
    """
    def _getter(key):
        keys = key.split(".")
        value = config
        for k in keys:
            if not isinstance(value, dict):
                raise KeyError(f"Config key '{key}' does not exist (hit non-dict at '{k}')")
            if k not in value:
                raise KeyError(f"Config key '{key}' does not exist (missing '{k}')")
            value = value[k]
        return value
    return _getter

def pytest_configure(config):
    config.addinivalue_line("markers", "smoke: mark test as smoke test")
