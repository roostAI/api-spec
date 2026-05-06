import pytest
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import yaml
import json
from pathlib import Path
import os
import re

CONFIG_FILE = Path(__file__).parent / "config.yml"

def _expand_env_vars(data):
    env_pattern = re.compile(r"\${([^}:s]+):-([^}]+)}")
    def replace_env(match):
        env_var, default = match.group(1), match.group(2)
        return os.environ.get(env_var, default)
    def expand_value(val):
        if isinstance(val, str):
            return env_pattern.sub(replace_env, val)
        elif isinstance(val, dict):
            return {k: expand_value(v) for k, v in val.items()}
        elif isinstance(val, list):
            return [expand_value(i) for i in val]
        else:
            return val
    return expand_value(data)

@pytest.fixture(scope="session")
def config():
    if not CONFIG_FILE.exists():
        pytest.exit(f"config.yml missing at {CONFIG_FILE.resolve()}")
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            raw_yaml = yaml.safe_load(f)
    except Exception as e:
        pytest.exit(f"Failed to load config.yml: {str(e)}")
    config_expanded = _expand_env_vars(raw_yaml)
    return config_expanded

@pytest.fixture
def load_endpoint_test_data(request):
    def loader(path):
        json_path = Path(path)
        if not json_path.exists():
            pytest.fail(f"Endpoint test data file not found: {json_path}")
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            pytest.fail(f"Failed to load endpoint test data: {str(e)}")
    return loader

@pytest.fixture
def merged_test_data(config, load_endpoint_test_data):
    def merger(path):
        endpoint_data = load_endpoint_test_data(path)
        config_data = config.get("test_data", {})
        merged = {**config_data, **endpoint_data}
        return merged
    return merger

class APIClient:
    def __init__(self, base_url, timeout=10, retries=3, headers=None):
        self.base_url = base_url.strip()
        self.timeout = timeout
        self.session = requests.Session()
        adapter = HTTPAdapter(max_retries=Retry(
            total=retries, backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504]
        ))
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        self.default_headers = headers or {}

    def make_request(self, endpoint, method="GET", headers=None, **kwargs):
        url = self.base_url.rstrip("/") + "/" + endpoint.lstrip("/")
        req_headers = {**self.default_headers, **(headers or {})}
        try:
            resp = self.session.request(
                method, url,
                headers=req_headers,
                timeout=self.timeout,
                **kwargs
            )
            resp.raise_for_status()
        except requests.RequestException as e:
            raise RuntimeError(f"API request failed: {e}")
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
    base_url = config["api"]["host"]
    timeout = int(config.get("api", {}).get("timeout", 10))
    retries = int(config.get("api", {}).get("retries", 3))
    headers = {}
    api_key_header = config.get("auth", {}).get("api_key_header")
    api_key_value = config.get("auth", {}).get("api_key_value")
    if api_key_header and api_key_value:
        headers[api_key_header] = api_key_value
    return APIClient(base_url, timeout=timeout, retries=retries, headers=headers)

@pytest.fixture
def get_config(config):
    def getter(dotted_key):
        keys = dotted_key.split(".")
        curr = config
        for key in keys:
            if not isinstance(curr, dict) or key not in curr:
                return None
            curr = curr[key]
        return curr
    return getter

def pytest_configure(config):
    config.addinivalue_line("markers", "smoke: mark test as smoke test.")
