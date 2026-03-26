import os
import re
import pytest
import yaml
import json
import requests
from pathlib import Path
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

def _expand_env_vars(value):
    pattern = re.compile(r"\${([^}:]+):-([^}]+)}")
    def replacer(match):
        env_var, default = match.groups()
        return os.getenv(env_var, default)
    return pattern.sub(replacer, value)

def load_config():
    config_path = Path(__file__).parent / 'config.yml'
    if not config_path.exists():
        raise FileNotFoundError("config.yml not found")
    with config_path.open() as f:
        config = yaml.safe_load(f)
    return {k: _expand_env_vars(v) if isinstance(v, str) else v for k, v in config.items()}

@pytest.fixture(scope='session')
def config():
    return load_config()

@pytest.fixture
def load_endpoint_test_data():
    def _load(path):
        with open(path) as f:
            return json.load(f)
    return _load

@pytest.fixture
def merged_test_data(config, load_endpoint_test_data):
    def _merge(path):
        endpoint_data = load_endpoint_test_data(path)
        merged_data = config.get('test_data', {}).copy()
        merged_data.update(endpoint_data)
        return merged_data
    return _merge

class APIClient:
    def __init__(self, base_url):
        self.base_url = base_url.strip()
        self.session = requests.Session()
        retries = Retry(total=3, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
        self.session.mount('http://', HTTPAdapter(max_retries=retries))
        self.session.mount('https://', HTTPAdapter(max_retries=retries))

    def make_request(self, endpoint, method="GET", headers=None, **kwargs):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = self.session.request(method, url, headers=headers, **kwargs)
        response.raise_for_status()
        return response

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
    base_url = config["api"]["host"]
    return APIClient(base_url)

@pytest.fixture
def get_config(config):
    def _get(key):
        keys = key.split('.')
        value = config
        for k in keys:
            value = value.get(k)
            if value is None:
                break
        return value
    return _get

def pytest_configure(config):
    config.addinivalue_line("markers", "smoke: mark test as smoke test")
