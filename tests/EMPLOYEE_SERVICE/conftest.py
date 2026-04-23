import os
import re
import pytest
import yaml
import json
import requests
from pathlib import Path
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# -------------- 1. CONFIGURATION LOADING -------------- #

def _expand_env_vars(s):
    # Pattern: ${ENV_VAR:-default}
    # group(1): ENV_VAR, group(2): default
    pattern = re.compile(r"\$\{([^}:]+):-([^}]+)\}")
    def repl(match):
        env_var = match.group(1)
        default = match.group(2)
        return os.environ.get(env_var, default)
    if isinstance(s, str):
        # Only process if string
        return pattern.sub(repl, s)
    return s

def _expand_dict_env_vars(obj):
    # Recursively expand all strings in dict/list
    if isinstance(obj, dict):
        return {k: _expand_dict_env_vars(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_expand_dict_env_vars(i) for i in obj]
    else:
        return _expand_env_vars(obj)

@pytest.fixture(scope="session")
def config():
    config_path = Path(__file__).parent / "config.yml"
    if not config_path.exists():
        raise FileNotFoundError(f"config.yml not found at {config_path}")
    try:
        with open(config_path, "r") as f:
            cfg = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise RuntimeError(f"Could not parse config.yml: {e}")
    cfg = _expand_dict_env_vars(cfg)
    return cfg

# -------------- 2. ENDPOINT TEST DATA LOADING/OVERRIDE ------------- #

@pytest.fixture
def load_endpoint_test_data():
    def _loader(path):
        json_path = Path(path)
        if not json_path.exists():
            raise FileNotFoundError(f"Endpoint test data file {json_path} not found")
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            raise RuntimeError(f"Could not load endpoint test data from {json_path}: {e}")
        return data
    return _loader

@pytest.fixture
def merged_test_data(config, load_endpoint_test_data):
    def _merger(endpoint_json_path):
        config_td = config.get("test_data", {}) or {}
        endpoint_td = load_endpoint_test_data(endpoint_json_path) or {}
        merged = dict(config_td)  # copy config test data
        merged.update(endpoint_td)  # endpoint overrides config
        return merged
    return _merger

# -------------- 3. API CLIENT FIXTURE -------------- #

class APIClient:
    def __init__(self, base_url, headers=None, timeout=15, retry_total=3, retry_backoff=0.2, retry_statuses=(500, 502, 503, 504)):
        self.base_url = base_url.strip().rstrip("/")
        self.session = requests.Session()
        retries = Retry(
            total=retry_total,
            backoff_factor=retry_backoff,
            status_forcelist=list(retry_statuses),
            allowed_methods=frozenset(['GET', 'POST', 'PUT', 'PATCH', 'DELETE']),
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        self.default_headers = headers or {}
        self.timeout = timeout

    def make_request(self, endpoint, method="GET", headers=None, **kwargs):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        req_headers = dict(self.default_headers)
        if headers:
            req_headers.update(headers)
        timeout = kwargs.pop("timeout", self.timeout)
        resp = self.session.request(
            method=method,
            url=url,
            headers=req_headers,
            timeout=timeout,
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
    base_url = config["api"]["host"].strip()
    # Check for optional headers (such as API Key via config['auth'])
    default_headers = {}
    auth_config = config.get("auth", {})
    api_key_header = auth_config.get("api_key_header")
    api_key_value = auth_config.get("api_key")
    if api_key_header and api_key_value:
        default_headers[api_key_header] = api_key_value
    timeout = int(config["api"].get("timeout", 15)) if "timeout" in config.get("api", {}) else 15
    retry_total = int(config["api"].get("retry_total", 3)) if "retry_total" in config.get("api", {}) else 3
    retry_backoff = float(config["api"].get("retry_backoff", 0.2)) if "retry_backoff" in config.get("api", {}) else 0.2
    return APIClient(
        base_url=base_url,
        headers=default_headers,
        timeout=timeout,
        retry_total=retry_total,
        retry_backoff=retry_backoff,
    )

# -------------- 4. DYNAMIC CONFIG GETTER -------------- #

@pytest.fixture
def get_config(config):
    def _getter(key_path, default=None):
        keys = key_path.split(".")
        val = config
        for k in keys:
            if isinstance(val, dict) and k in val:
                val = val[k]
            else:
                return default
        return val
    return _getter

# -------------- 5. TEST MARKERS -------------- #

def pytest_configure(config):
    config.addinivalue_line(
        "markers", "smoke: mark test as a smoke (basic health) test"
    )
