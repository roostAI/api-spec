import pytest
import requests
import yaml
import json
import os
import re
from pathlib import Path
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def pytest_configure(config):
    config.addinivalue_line("markers", "smoke: mark test as smoke test")


def _expand_env_vars(value):
    """Expand environment variables in the format ${VAR:-default}"""
    if not isinstance(value, str):
        return value
    
    pattern = r'\$\{([^}:\s]+):-([^}]*)\}'
    
    def replace_env_var(match):
        env_var = match.group(1)
        default_value = match.group(2)
        return os.environ.get(env_var, default_value)
    
    return re.sub(pattern, replace_env_var, value)


def _expand_config_values(config_dict):
    """Recursively expand environment variables in config dictionary"""
    if isinstance(config_dict, dict):
        return {key: _expand_config_values(value) for key, value in config_dict.items()}
    elif isinstance(config_dict, list):
        return [_expand_config_values(item) for item in config_dict]
    else:
        return _expand_env_vars(config_dict)


@pytest.fixture(scope="session")
def config():
    """Load and parse config.yml with environment variable expansion"""
    config_path = Path(__file__).parent / "config.yml"
    
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    try:
        with open(config_path, 'r') as file:
            config_data = yaml.safe_load(file)
        
        if config_data is None:
            raise ValueError("Config file is empty or invalid")
        
        return _expand_config_values(config_data)
    
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in config file: {e}")
    except Exception as e:
        raise RuntimeError(f"Error loading config: {e}")


@pytest.fixture
def load_endpoint_test_data(request):
    """Load endpoint test data from JSON file"""
    def _load_data(path):
        if isinstance(path, str):
            json_path = Path(path)
        else:
            json_path = Path(path)
        
        if not json_path.exists():
            raise FileNotFoundError(f"Test data file not found: {json_path}")
        
        try:
            with open(json_path, 'r') as file:
                return json.load(file)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in test data file: {e}")
        except Exception as e:
            raise RuntimeError(f"Error loading test data: {e}")
    
    return _load_data


@pytest.fixture
def merged_test_data(config, load_endpoint_test_data):
    """Merge config test_data with endpoint test data, with endpoint data taking precedence"""
    def _merge_data(endpoint_data_path=None):
        base_data = config.get("test_data", {}).copy()
        
        if endpoint_data_path:
            endpoint_data = load_endpoint_test_data(endpoint_data_path)
            base_data.update(endpoint_data)
        
        return base_data
    
    return _merge_data


@pytest.fixture
def get_config(config):
    """Get config value by dotted key path"""
    def _get_config_value(key_path):
        keys = key_path.split('.')
        value = config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                raise KeyError(f"Config key not found: {key_path}")
        
        return value
    
    return _get_config_value


class APIClient:
    """Simple API client with retry and timeout support"""
    
    def __init__(self, base_url, timeout=30, retries=3):
        self.base_url = base_url.strip()
        self.timeout = timeout
        self.session = requests.Session()
        
        retry_strategy = Retry(
            total=retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def make_request(self, endpoint, method="GET", headers=None, **kwargs):
        """Make HTTP request to the API"""
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        kwargs.setdefault('timeout', self.timeout)
        if headers:
            kwargs.setdefault('headers', {}).update(headers)
        
        response = self.session.request(method, url, **kwargs)
        return response
    
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


@pytest.fixture
def api_client(config):
    """Create API client instance using config"""
    base_url = config["api"]["host"]
    return APIClient(base_url)
