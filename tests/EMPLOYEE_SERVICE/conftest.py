import pytest
import os
import re
import yaml
import json
from pathlib import Path
import requests
from requests.adapters import HTTPAdapter, Retry

_CONFIG_PATH = Path(__file__).parent / "config.yml"
_ENV_VAR_REGEX = r"\${([^}:]+):-([^}]+)}"

def _expand_env_vars(obj):
    """
    Recursively expand env var patterns of form ${ENV_VAR:-default} in strings within obj.
    """
    if isinstance(obj, dict):
        return {k: _expand_env_vars(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_expand_env_vars(v) for v in obj]
    elif isinstance(obj, str):
        def replacer(match):
            env_var, default = match.group(1), match.group(2)
            return os.environ.get(env_var, default)
        return re.sub(_ENV_VAR_REGEX, replacer, obj)
    else:
        return obj

def _get_by_dotted_key(dct, dotted):
    keys = dotted.split('.')
    value = dct
    for key in keys:
        value = value[key]
    return value

@pytest.fixture(scope="session")
def config():
    if not _CONFIG_PATH.exists():
        raise FileNotFoundError(f"Config file not found: {_CONFIG_PATH}")
    try:
        with _CONFIG_PATH.open("r", encoding="utf-8") as f:
            raw = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise RuntimeError(f"Invalid yaml in config.yml: {e}")
    config = _expand_env_vars(raw)
    return config

@pytest.fixture
def load_endpoint_test_data():
    """
    Fixture that loads endpoint test data JSON from a specified path.
    """
    def _loader(path):
        p = Path(path)
        if not p.is_file():
            raise FileNotFoundError(f"Test data file not found: {path}")
        try:
            with p.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Invalid JSON in test data file {path}: {e}")
        return data
    return _loader

@pytest.fixture
def merged_test_data(config, load_endpoint_test_data):
    """
    Fixture that merges config['test_data'] and endpoint test data,
    endpoint test data overrides config if keys overlap.
    Usage: merged_test_data(endpoint_json_path)
    """
    def _merger(endpoint_json_path):
        config_td = dict(config.get('test_data') or {})
        endpoint_td = load_endpoint_test_data(endpoint_json_path)
        merged = {**config_td, **endpoint_td}
        return merged
    return _merger

class APIClient:
    def __init__(self, base_url, timeout=10, retries=3, backoff_factor=0.4):
        self.base_url = base_url.strip().rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        adapter = HTTPAdapter(
            max_retries=Retry(
                total=retries,
                backoff_factor=backoff_factor,
                status_forcelist=[502, 503, 504, 429],
                allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST", "PATCH"]
            )
        )
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

    def make_request(self, endpoint, method="GET", headers=None, **kwargs):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        return self.session.request(
            method=method,
            url=url,
            headers=headers,
            timeout=self.timeout,
            **kwargs
        )

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
    api_conf = config['api']
    base_url = api_conf['host']
    timeout = int(api_conf.get('timeout', 10))
    retries = int(api_conf.get('retries', 3))
    backoff_factor = float(api_conf.get('backoff_factor', 0.4))
    client = APIClient(
        base_url=base_url,
        timeout=timeout,
        retries=retries,
        backoff_factor=backoff_factor
    )
    return client

@pytest.fixture
def get_config(config):
    """
    Returns a function to get a config value by dotted key.
    """
    def _getter(dotted_key):
        try:
            return _get_by_dotted_key(config, dotted_key)
        except KeyError:
            raise KeyError(f"Key '{dotted_key}' not found in config.yml")
    return _getter

def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "smoke: mark test as smoke test"
    )
