import pytest
import requests
import yaml
import json
import os
import re
from pathlib import Path
from requests.adapters import HTTPAdapter, Retry

def _expand_env_vars(obj):
    pattern = re.compile(r"\${([^}:]+):-([^}]+)}")
    if isinstance(obj, dict):
        return {k: _expand_env_vars(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_expand_env_vars(i) for i in obj]
    elif isinstance(obj, str):
        def replacer(match):
            env_name = match.group(1)
            default = match.group(2)
            return os.environ.get(env_name, default)
        while True:
            new_obj = pattern.sub(replacer, obj)
            if new_obj == obj:
                break
            obj = new_obj
        return obj
    else:
        return obj

@pytest.fixture(scope="session")
def config():
    config_path = Path(__file__).parent / "config.yml"
    if not config_path.is_file():
        raise FileNotFoundError(f"Missing config.yml at: {config_path}")
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f)
        if raw is None:
            raw = {}
    except yaml.YAMLError as e:
        raise RuntimeError(f"config.yml parse error: {e}")
    return _expand_env_vars(raw)

@pytest.fixture
def load_endpoint_test_data():
    def loader(path):
        data_path = Path(path)
        if not data_path.is_file():
            raise FileNotFoundError(f"Test data JSON not found: {data_path}")
        try:
            with open(data_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                raise ValueError("Endpoint test data must be a JSON object (dict).")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Invalid JSON file {data_path}: {e}")
        return data
    return loader

@pytest.fixture
def merged_test_data(config, load_endpoint_test_data):
    def merger(json_path):
        yaml_data = config.get("test_data", {}) if isinstance(config, dict) else {}
        try:
            endpoint_data = load_endpoint_test_data(json_path)
        except FileNotFoundError:
            return yaml_data.copy()
        if not isinstance(endpoint_data, dict):
            raise ValueError(f"JSON from {json_path} must be a dict.")
        merged = dict(yaml_data)
        merged.update(endpoint_data)
        return merged
    return merger

class APIClient:
    def __init__(self, base_url, timeout=10, retry=3, backoff_factor=0.5, headers=None):
        self.base_url = base_url.rstrip().rstrip('/')
        self.timeout = float(timeout)
        self.session = requests.Session()
        adapter = HTTPAdapter(max_retries=Retry(
            total=retry,
            backoff_factor=backoff_factor,
            status_forcelist=[502, 503, 504, 429],
            allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST", "PATCH"]
        ))
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        self.default_headers = headers or {}

    def make_request(self, endpoint, method="GET", headers=None, **kwargs):
        url = self.base_url + '/' + endpoint.lstrip("/")
        req_headers = dict(self.default_headers)
        if headers:
            req_headers.update(headers)
        resp = self.session.request(
            method=method.upper(),
            url=url,
            headers=req_headers,
            timeout=self.timeout,
            **kwargs
        )
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
    api_cfg = config.get('api', {})
    base_url = api_cfg.get('host', '').strip()
    if not base_url:
        raise ValueError("api.host missing or empty in config")
    timeout = api_cfg.get('timeout', 10)
    retry = api_cfg.get('retry', 3)
    backoff = api_cfg.get('backoff_factor', 0.5)
    default_headers = {}
    auth_cfg = config.get('auth', {})
    if "api_key_header" in auth_cfg and "api_key" in auth_cfg:
        default_headers[auth_cfg["api_key_header"]] = auth_cfg["api_key"]
    return APIClient(
        base_url=base_url,
        timeout=timeout,
        retry=retry,
        backoff_factor=backoff,
        headers=default_headers
    )

@pytest.fixture
def get_config(config):
    def getter(dotted_key, default=None):
        keys = dotted_key.split('.')
        val = config
        for k in keys:
            if not isinstance(val, dict) or k not in val:
                return default
            val = val[k]
        return val
    return getter

def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "smoke: mark test as a smoke test"
    )
