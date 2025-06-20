import os
import yaml
import json
import requests
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from pathlib import Path
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class Environment(Enum):
    """Supported environments"""
    DEV = "dev"
    UAT = "uat"
    PROD = "prod"


@dataclass
class MetadataConfig:
    """Environment-specific configuration loaded from JSON file"""
    name: str
    api_base_url: str
    api_timeout: int = 30
    yaml_path: Optional[str] = None
    api_auth_token_env_key: str = "API_TOKEN"  # Environment variable key for API token
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MetadataConfig':
        """Create MetadataConfig from dictionary"""
        return cls(
            name=data.get('name', ''),
            api_base_url=data.get('api_base_url', ''),
            api_timeout=data.get('api_timeout', 30),
            yaml_path=data.get('yaml_path'),
            api_auth_token_env_key=data.get('api_auth_token_env_key', 'API_TOKEN')
        )


class EnvironmentResolver:
    """Resolves environment configuration based on DSF_DOMAIN"""
    
    # Mapping of DSF_DOMAIN values to environment names
    DOMAIN_MAPPING = {
        'D': Environment.DEV,
        'U': Environment.UAT,
        'P': Environment.PROD
    }
    
    def __init__(self, config_path: str = "config/environments.json"):
        self.config_path = config_path
        self._configs: Dict[Environment, MetadataConfig] = {}
        self._load_configs()
    
    def _load_configs(self) -> None:
        """Load all environment configurations from JSON file"""
        config_file = Path(self.config_path)
        if not config_file.exists():
            logger.warning(f"Environment config file not found: {self.config_path}")
            return
        
        try:
            with open(config_file, 'r') as f:
                data = json.load(f)
                
            for env_key, env_data in data.items():
                if env_key in ['dev', 'uat', 'prod']:
                    env = Environment(env_key)
                    self._configs[env] = MetadataConfig.from_dict(env_data)
                    
        except Exception as e:
            logger.error(f"Failed to load environment config: {e}")
    
    def get_environment(self, dsf_domain: str) -> Environment:
        """Get environment enum based on DSF_DOMAIN value"""
        if dsf_domain not in self.DOMAIN_MAPPING:
            logger.warning(f"Unknown DSF_DOMAIN value: {dsf_domain}, defaulting to DEV")
            return Environment.DEV
        
        return self.DOMAIN_MAPPING[dsf_domain]
    
    def get_config(self, dsf_domain: str) -> MetadataConfig:
        """Get MetadataConfig for the given DSF_DOMAIN"""
        env = self.get_environment(dsf_domain)
        
        if env not in self._configs:
            # Return default config if not found
            return MetadataConfig(
                name=env.value,
                api_base_url=f"https://metadata-api-{env.value}.azure.com"
            )
        
        return self._configs[env]


class MetadataSource(ABC):
    """Abstract base class for metadata sources"""
    
    @abstractmethod
    def fetch(self, key: str) -> Optional[Any]:
        """Fetch metadata value by key"""
        pass
    
    @abstractmethod
    def fetch_all(self) -> Dict[str, Any]:
        """Fetch all metadata from this source"""
        pass
    
    @abstractmethod
    def refresh(self) -> None:
        """Refresh/reload metadata from source"""
        pass


class EnvironmentMetadataSource(MetadataSource):
    """Metadata source for environment variables"""
    
    def __init__(self, prefix: str = ""):
        self.prefix = prefix
    
    def fetch(self, key: str) -> Optional[Any]:
        """Fetch from environment with optional prefix"""
        env_key = f"{self.prefix}{key}" if self.prefix else key
        return os.environ.get(env_key)
    
    def fetch_all(self) -> Dict[str, Any]:
        """Return all environment variables with the prefix"""
        result = {}
        for key, value in os.environ.items():
            if self.prefix and key.startswith(self.prefix):
                # Remove prefix for cleaner access
                clean_key = key[len(self.prefix):]
                result[clean_key] = value
            elif not self.prefix:
                result[key] = value
        return result
    
    def refresh(self) -> None:
        """No-op for environment variables"""
        pass


class YamlMetadataSource(MetadataSource):
    """Metadata source for YAML configuration files"""
    
    def __init__(self, yaml_path: str):
        self.yaml_path = Path(yaml_path)
        self._data: Dict[str, Any] = {}
        if self.yaml_path.exists():
            self.refresh()
    
    def fetch(self, key: str) -> Optional[Any]:
        """Fetch value using dot notation (e.g., 'pipeline.name')"""
        keys = key.split('.')
        value = self._data
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return None
        
        return value
    
    def fetch_all(self) -> Dict[str, Any]:
        """Return all YAML data"""
        return self._data.copy()
    
    def refresh(self) -> None:
        """Reload YAML file"""
        try:
            with open(self.yaml_path, 'r') as f:
                self._data = yaml.safe_load(f) or {}
        except Exception as e:
            logger.error(f"Failed to load YAML from {self.yaml_path}: {e}")
            self._data = {}


class ApiMetadataSource(MetadataSource):
    """Metadata source for API endpoints with support for nested JSON queries"""
    
    def __init__(self, base_url: str, auth_token: Optional[str] = None, 
                 timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.auth_token = auth_token
        self.timeout = timeout
        self._headers = {}
        self._api_data: Dict[str, Any] = {}
        
        if self.auth_token:
            self._headers['Authorization'] = f"Bearer {self.auth_token}"
        
        # Fetch all metadata on initialization
        self._load_api_data()
    
    def _load_api_data(self) -> None:
        """Load all metadata from API endpoint"""
        try:
            endpoint = f"{self.base_url}/metadata"
            response = requests.get(
                endpoint,
                headers=self._headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            self._api_data = response.json()
            logger.info(f"Successfully loaded API metadata from {endpoint}")
        except Exception as e:
            logger.error(f"Failed to load API metadata: {e}")
            self._api_data = {}
    
    def _navigate_nested_dict(self, data: Dict[str, Any], keys: List[str]) -> Any:
        """Navigate through nested dictionary using a list of keys"""
        current = data
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        return current
    
    def _query_list(self, items: List[Dict[str, Any]], conditions: Dict[str, Any]) -> List[Any]:
        """Query a list of dictionaries based on conditions"""
        results = []
        for item in items:
            if all(item.get(k) == v for k, v in conditions.items()):
                results.append(item)
        return results
    
    def fetch(self, key: str) -> Optional[Any]:
        """
        Fetch metadata using various query patterns:
        - Simple key: 'swci' -> returns value
        - Nested key: 'resourceGroup' -> returns value
        - Dot notation: 'servicePrinciples.0.name' -> returns specific item
        - Query syntax: 'servicePrinciples[bookingCenter=001].name' -> returns filtered results
        - List field extraction: 'storageContainers[bookingCenterCode=001].storageName' -> returns list of values
        """
        if not self._api_data:
            return None
        
        # Handle query syntax: 'path[field=value].targetField'
        if '[' in key and ']' in key:
            return self._handle_query_syntax(key)
        
        # Handle dot notation for nested access
        if '.' in key:
            keys = key.split('.')
            return self._navigate_nested_dict(self._api_data, keys)
        
        # Simple key access
        return self._api_data.get(key)
    
    def _handle_query_syntax(self, query: str) -> Optional[Any]:
        """
        Handle query syntax like 'servicePrinciples[bookingCenter=001].name'
        Returns single value, list of values, or list of objects based on query
        """
        import re
        
        # Parse the query pattern
        match = re.match(r'([^[]+)\[([^]]+)\](?:\.(.+))?', query)
        if not match:
            return None
        
        list_path, conditions_str, target_field = match.groups()
        
        # Get the list to query
        list_data = self._api_data.get(list_path)
        if not isinstance(list_data, list):
            return None
        
        # Parse conditions
        conditions = {}
        for condition in conditions_str.split(','):
            if '=' in condition:
                field, value = condition.strip().split('=', 1)
                conditions[field.strip()] = value.strip()
        
        # Filter the list based on conditions
        filtered_items = self._query_list(list_data, conditions)
        
        if not filtered_items:
            return None
        
        # Extract target field if specified
        if target_field:
            results = []
            for item in filtered_items:
                value = self._navigate_nested_dict(item, target_field.split('.'))
                if value is not None:
                    results.append(value)
            
            # Return single value if only one result, otherwise return list
            if len(results) == 1:
                return results[0]
            return results if results else None
        
        # Return the filtered objects if no target field specified
        return filtered_items if len(filtered_items) > 1 else filtered_items[0]
    
    def fetch_all(self) -> Dict[str, Any]:
        """Return all API metadata"""
        return self._api_data.copy()
    
    def refresh(self) -> None:
        """Reload metadata from API"""
        self._load_api_data()


class Metadata:
    """Main metadata manager that aggregates all sources"""
    
    def __init__(self, environment_config_path: str = "config/environments.json"):
        """
        Initialize Metadata manager
        
        Args:
            environment_config_path: Path to environment configuration JSON
        """
        self._sources: Dict[str, MetadataSource] = {}
        
        # Step 1: Initialize environment source first (no prefix)
        self._sources['env'] = EnvironmentMetadataSource(prefix="")
        
        # Step 2: Get DSF_DOMAIN from the already loaded environment source
        dsf_domain = self._sources['env'].fetch('DSF_DOMAIN')
        if dsf_domain is None:
            logger.warning("DSF_DOMAIN not found in environment, defaulting to 'D'")
            dsf_domain = 'D'
        self.dsf_domain = dsf_domain
        
        # Step 3: Load environment-specific configuration
        resolver = EnvironmentResolver(environment_config_path)
        self.config = resolver.get_config(dsf_domain)
        
        # Step 4: Initialize other sources based on loaded config
        self._initialize_additional_sources()
    
    def _initialize_additional_sources(self) -> None:
        """Initialize YAML and API sources based on MetadataConfig"""
        
        # Add YAML source if configured
        yaml_path = self.config.yaml_path or "config/pipeline.yaml"
        if Path(yaml_path).exists():
            self._sources['yaml'] = YamlMetadataSource(yaml_path)
        
        # Add API source if configured
        if self.config.api_base_url:
            # Get API token from environment using the configured key
            api_token = self._sources['env'].fetch(self.config.api_auth_token_env_key)
            
            self._sources['api'] = ApiMetadataSource(
                base_url=self.config.api_base_url,
                auth_token=api_token,
                timeout=self.config.api_timeout
            )
    
    def get(self, key: str, default: Any = None, 
            source: Optional[str] = None) -> Any:
        """
        Get metadata value by key.
        
        Args:
            key: The metadata key to fetch
            default: Default value if key not found
            source: Specific source to fetch from (env, yaml, api)
                   If None, searches all sources in order
        
        Returns:
            The metadata value or default
        """
        value = None
        
        if source:
            # Fetch from specific source
            if source in self._sources:
                value = self._sources[source].fetch(key)
        else:
            # Search all sources in priority order: env -> yaml -> api
            for source_name in ['env', 'yaml', 'api']:
                if source_name in self._sources:
                    value = self._sources[source_name].fetch(key)
                    if value is not None:
                        break
        
        return value if value is not None else default
    
    def get_required(self, key: str, source: Optional[str] = None) -> Any:
        """Get required metadata value, raise exception if not found"""
        value = self.get(key, source=source)
        if value is None:
            source_msg = f" in source '{source}'" if source else ""
            raise ValueError(f"Required metadata key '{key}' not found{source_msg}")
        return value
    
    def get_batch(self, keys: List[str], 
                  source: Optional[str] = None) -> Dict[str, Any]:
        """Fetch multiple keys at once"""
        return {key: self.get(key, source=source) for key in keys}
    
    def refresh(self, source: Optional[str] = None) -> None:
        """Refresh metadata from sources"""
        if source:
            if source in self._sources:
                self._sources[source].refresh()
        else:
            for src in self._sources.values():
                src.refresh()
    
    def get_all(self, source: Optional[str] = None) -> Dict[str, Any]:
        """Get all metadata from a specific source or all sources"""
        if source and source in self._sources:
            return self._sources[source].fetch_all()
        
        # Merge all sources (later sources override earlier ones)
        all_metadata = {}
        for source_name in ['api', 'yaml', 'env']:  # Reverse priority
            if source_name in self._sources:
                all_metadata.update(self._sources[source_name].fetch_all())
        
        return all_metadata
    
    @property
    def sources(self) -> List[str]:
        """List available metadata sources"""
        return list(self._sources.keys())
    
    @property
    def current_environment(self) -> str:
        """Get current environment name"""
        return self.config.name


# Example usage
if __name__ == "__main__":
    # Set environment variables for testing
    os.environ['DSF_DOMAIN'] = 'U'  # UAT environment
    os.environ['API_TOKEN'] = 'secure-api-token-123'
    os.environ['WAREHOUSE_HOST'] = 'warehouse.uat.company.com'
    
    # Initialize metadata - DSF_DOMAIN is read from environment source
    metadata = Metadata(environment_config_path="config/environments.json")
    
    print(f"Current environment: {metadata.current_environment}")
    print(f"Config loaded:")
    print(f"  - API URL: {metadata.config.api_base_url}")
    print(f"  - API Timeout: {metadata.config.api_timeout}")
    print(f"  - YAML Path: {metadata.config.yaml_path}")
    
    # Example API queries
    # Simple key access
    swci = metadata.get("swci", source="api")
    print(f"\nSWCI: {swci}")
    
    # Query with condition - get service principle name for booking center 001
    sp_name = metadata.get("servicePrinciples[bookingCenter=001].name", source="api")
    print(f"Service Principle Name: {sp_name}")
    
    # Query returning multiple values - get all storage names for booking center 001
    storage_names = metadata.get("storageContainers[bookingCenterCode=001].storageName", source="api")
    print(f"Storage Names: {storage_names}")
    
    # Get entire filtered object
    job = metadata.get("jobs[name=job1]", source="api")
    print(f"Job: {job}")
    
    # Regular metadata access
    warehouse_host = metadata.get("WAREHOUSE_HOST", source="env")
    pipeline_name = metadata.get("pipeline.name", source="yaml")
    
    print(f"\nWarehouse Host: {warehouse_host}")
    print(f"Pipeline Name: {pipeline_name}")
    print(f"Available sources: {metadata.sources}")