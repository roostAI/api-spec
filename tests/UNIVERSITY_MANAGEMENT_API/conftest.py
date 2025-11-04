import os
import re
import pytest
import requests
import yaml
from pathlib import Path
from typing import Any, Dict, Optional, Union

# --- Configuration Loading ---

def _replace_env_vars(val: Any) -> Any:
    """Recursively replace environment variables in config values."""
    if isinstance(val, str):
        matches = re.findall(r'\$\{([^}]+)\}', val)
        for match in matches:
            env_var = os.getenv(match)
            if env_var is None:
                raise ValueError(f"Environment variable '{match}' not found.")
            val = val.replace(f'${{{match}}}', env_var)
        return val
    elif isinstance(val, dict):
        return {k: _replace_env_vars(v) for k, v in val.items()}
    elif isinstance(val, list):
        return [_replace_env_vars(i) for i in val]
    return val

@pytest.fixture(scope="session")
def config() -> Dict[str, Any]:
    """Loads configuration from config.yml and resolves environment variables."""
    config_path = os.path.join(Path(__file__).parent, 'config.yml')
    try:
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        return _replace_env_vars(config_data)
    except FileNotFoundError:
        pytest.fail(f"Configuration file not found at: {config_path}", pytrace=False)
    except yaml.YAMLError as e:
        pytest.fail(f"Error parsing YAML configuration file: {e}", pytrace=False)
    except ValueError as e:
        pytest.fail(str(e), pytrace=False)

# --- API Helpers and Clients ---

class APIHelper:
    """A helper class for making generic HTTP requests."""
    def __init__(self, base_url: str):
        self.base_url = base_url.strip()

    def make_request(
        self,
        endpoint: str,
        method: str = 'GET',
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> requests.Response:
        """
        Makes an HTTP request to the specified endpoint.

        Args:
            endpoint: The API endpoint path.
            method: HTTP method (e.g., 'GET', 'POST').
            params: URL parameters.
            headers: Request headers.
            json: JSON body for the request.
            data: Form data for the request.

        Returns:
            The requests.Response object.
        """
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        return requests.request(
            method=method,
            url=url,
            params=params,
            headers=headers,
            json=json,
            data=data
        )

class APIClient:
    """A simple API client for common operations."""
    def __init__(self, base_url: str):
        self.base_url = base_url.strip()

    def get(
        self,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> requests.Response:
        """
        Performs a GET request.

        Args:
            endpoint: The API endpoint path.
            headers: Request headers.
            params: URL parameters.

        Returns:
            The requests.Response object.
        """
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        return requests.get(url, headers=headers, params=params)


@pytest.fixture(scope="session")
def api_helper(config: Dict[str, Any]) -> APIHelper:
    """Fixture to provide an instance of the APIHelper."""
    base_url = config.get('api', {}).get('host')
    if not base_url:
        pytest.fail("API host not configured in config.yml", pytrace=False)
    return APIHelper(base_url)

@pytest.fixture(scope="session")
def api_client(config: Dict[str, Any]) -> APIClient:
    """Fixture to provide an instance of the APIClient."""
    base_url = config.get('api', {}).get('host')
    if not base_url:
        pytest.fail("API host not configured in config.yml", pytrace=False)
    return APIClient(base_url)


# --- Authentication and Parameter Fixtures ---

@pytest.fixture(scope="session")
def valid_api_key(config: Dict[str, Any]) -> str:
    """Provides a valid API key from the configuration."""
    key = config.get('api', {}).get('key')
    if not key:
        pytest.fail("API key not configured in config.yml", pytrace=False)
    return key

@pytest.fixture(scope="session")
def invalid_api_key() -> str:
    """Provides a dummy invalid API key."""
    return "invalid_api_key_for_testing"

@pytest.fixture(scope="session")
def valid_location() -> str:
    """Provides a valid test location parameter."""
    return "New York, NY"

@pytest.fixture(scope="session")
def oauth2_token(config: Dict[str, Any]) -> str:
    """Provides an OAuth2 token from the configuration."""
    token = config.get('api', {}).get('oauth2_token')
    if not token:
        pytest.fail("OAuth2 token not configured in config.yml", pytrace=False)
    return token

# --- Schema Validation ---

class SchemaValidator:
    """
    Contains methods to validate API response schemas.
    Each method corresponds to a schema definition from the component schema.
    Since the provided component schema content was empty, no methods are generated.
    """
    pass


@pytest.fixture(scope="session")
def schema_validator() -> SchemaValidator:
    """Fixture to provide an instance of the SchemaValidator."""
    return SchemaValidator()
