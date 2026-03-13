import os
import re
import yaml
import json
import pytest
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from pathlib import Path

class APIClient:
    def __init__(self, base_url, timeout=5, retries=3):
        self.base_url = base_url
        self.session = requests.Session()
        retry_strategy = Retry(total=retries, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        self.timeout = timeout

    def make_request(self, endpoint, method="GET", headers=None, **kwargs):
        url = self.base_url + endpoint
        return self.session.request(method, url, headers=headers, timeout=self.timeout, **kwargs)

    def get(self, endpoint, **kwargs):
        return self.make_request(endpoint, "GET", **kwargs)

    def post(self, endpoint, **kwargs):
        return self.make_request(endpoint, "POST", **kwargs)

    def put(self, endpoint, **kwargs):
        return self.make_request(endpoint, "PUT", **kwargs)

    def patch(self, endpoint, **kwargs):
        return self.make_request(endpoint, "PATCH", **kwargs)

    def delete(self, endpoint, **kwargs):
        return self.make_request(endpoint, "DELETE", **kwargs)

def _expand_env_vars(data):
    pattern = re.compile(r"\$\{([^}:\s]+):?-([^}]*)\}")
    return pattern.sub(lambda m: os.environ.get(m.group(1), m.group(2)), data)

@pytest.fixture(scope="session")
def config():
    config_path = Path(__file__).parent / "config.yml"
    try:
        with open(config_path, "r") as file:
            config = yaml.safe_load(file)
    except Exception as e:
        raise Exception(f"Failed to load config.yml: {e}")
    return {k: _expand_env_vars(v) if isinstance(v, str) else v for k, v in config.items()}

@pytest.fixture
def load_endpoint_test_data(request):
    path = request.param
    try:
        with open(path, "r") as file:
            return json.load(file)
    except Exception as e:
        raise Exception(f"Failed to load endpoint test data: {e}")

@pytest.fixture
def merged_test_data(config, load_endpoint_test_data):
    test_data = {**config.get("test_data", {}), **load_endpoint_test_data}
    return test_data

@pytest.fixture
def api_client(config):
    return APIClient(config["api"]["host"].strip())

@pytest.fixture
def get_config(config):
    def _get_config(key):
        keys = key.split(".")
        value = config
        for k in keys:
            value = value.get(k)
        return value
    return _get_config

def pytest_configure(config):
    config.addinivalue_line("markers", "smoke: mark test as smoke")
