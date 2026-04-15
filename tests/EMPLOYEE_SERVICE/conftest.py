import pytest
import requests
import yaml
import json
import os
import re
from pathlib import Path
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

CONFIG_FILE = Path(__file__).parent / "config.yml"

def _expand_env_vars(obj):
    pattern = re.compile(r"\${([^}:s]+):-([^}]+)}")
    if isinstance(obj, dict):
        return {k: _expand_env_vars(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_expand_env_vars(i) for i in obj]
    elif isinstance(obj, str):
        def replacer(match):
            env_var, default = match.group(1), match.group(2)
            return os.environ.get(env_var, default)
        return pattern.sub(replacer, obj)
    else:
        return obj

def _load_config():
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(f"config.yml not found at {CONFIG_FILE}")
    try:
        with open(CONFIG_FILE, "r", encoding='utf-8') as f:
            cfg = yaml.safe_load(f)
            if cfg is None:
                raise ValueError("config.yml is empty or invalid")
            return _expand_env_vars(cfg)
    except Exception as e:
        raise RuntimeError(f"Failed to load config.yml: {e}")

@pytest.fixture(scope='session')
def config():
    return _load_config()

@pytest.fixture
def load_endpoint_test_data():
    def _loader(path):
        json_path = Path(path)
        if not json_path.exists():
            raise FileNotFoundError(f"Test data JSON not found: {json_path}")
        try:
            with open(json_path, "r", encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            raise RuntimeError(f"Failed to load endpoint test data from {json_path}: {e}")
    return _loader

@pytest.fixture
def merged_test_data(config, load_endpoint_test_data):
    def _merged(json_path):
        config_data = config.get("test_data", {})
        endpoint_data = load_endpoint_test_data(json_path)
        merged = dict(config_data)
        merged.update(endpoint_data)
        return merged
    return _merged

class APIClient:
    def __init__(self, config):
        self.base_url = str(config["api"]["host"]).strip()
        self.session = requests.Session()
        retries = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
        )
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        self.timeout = float(config.get("api", {}).get("timeout", 10))

    def make_request(self, endpoint, method="GET", headers=None, **kwargs):
        url = self.base_url.rstrip("/") + "/" + endpoint.lstrip("/")
        resp = self.session.request(method=method, url=url, headers=headers, timeout=self.timeout, **kwargs)
        resp.raise_for_status()
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
    return APIClient(config)

def _get_dotted(config, key):
    parts = key.split('.')
    val = config
    for p in parts:
        if isinstance(val, dict) and p in val:
            val = val[p]
        else:
            raise KeyError(f"Config key '{key}' not found at '{p}'")
    return val

@pytest.fixture
def get_config(config):
    def _getter(key):
        return _get_dotted(config, key)
    return _getter

def pytest_configure(config):
    config.addinivalue_line("markers", "smoke: mark test as smoke")
