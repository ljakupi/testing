import os
import yaml
import json
import requests
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class MetadataConfig:
    """Configuration for metadata sources"""
    yaml_path: Optional[str] = None
    api_base_url: Optional[str] = None
    api_auth_token: Optional[str] = None
    api_timeout: int = 30
    cache_ttl: int = 300  # Cache TTL in seconds
    env_prefix: str = "DATAOFFLOAD_"  # Prefix for environment variables


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
        self._cache = {}
        self.refresh()
    
    def fetch(self, key: str) -> Optional[Any]:
        """Fetch from environment with optional prefix"""
        env_key = f"{self.prefix}{key}" if self.prefix else key
        return self._cache.get(env_key)
    
    def fetch_all(self) -> Dict[str, Any]:
        """Return all environment variables with the prefix"""
        return self._cache.copy()
    
    def refresh(self) -> None:
        """Reload environment variables"""
        self._cache = {}
        for key, value in os.environ.items():
            if self.prefix and key.startswith(self.prefix):
                # Remove prefix for cleaner access
                clean_key = key[len(self.prefix):]
                self._cache[clean_key] = value
            elif not self.prefix:
                self._cache[key] = value


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
    """Metadata source for API endpoints"""
    
    def __init__(self, base_url: str, auth_token: Optional[str] = None, 
                 timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.auth_token = auth_token
        self.timeout = timeout
        self._cache: Dict[str, Any] = {}
        self._headers = {}
        
        if self.auth_token:
            self._headers['Authorization'] = f"Bearer {self.auth_token}"
    
    def fetch(self, key: str) -> Optional[Any]:
        """Fetch metadata from API endpoint"""
        if key in self._cache:
            return self._cache[key]
        
        try:
            endpoint = f"{self.base_url}/metadata/{key}"
            response = requests.get(
                endpoint,
                headers=self._headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            self._cache[key] = data
            return data
            
        except Exception as e:
            logger.error(f"Failed to fetch {key} from API: {e}")
            return None
    
    def fetch_all(self) -> Dict[str, Any]:
        """Fetch all metadata from API"""
        try:
            endpoint = f"{self.base_url}/metadata"
            response = requests.get(
                endpoint,
                headers=self._headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            self._cache.update(data)
            return data
            
        except Exception as e:
            logger.error(f"Failed to fetch all metadata from API: {e}")
            return self._cache.copy()
    
    def refresh(self) -> None:
        """Clear cache to force fresh API calls"""
        self._cache.clear()


class Metadata:
    """Main metadata manager that aggregates all sources"""
    
    def __init__(self, config: Optional[MetadataConfig] = None):
        self.config = config or MetadataConfig()
        self._sources: Dict[str, MetadataSource] = {}
        self._metadata_cache: Dict[str, Any] = {}
        
        # Initialize sources based on config
        self._initialize_sources()
    
    def _initialize_sources(self) -> None:
        """Initialize metadata sources based on configuration"""
        # Always add environment source
        self._sources['env'] = EnvironmentMetadataSource(
            prefix=self.config.env_prefix
        )
        
        # Add YAML source if configured
        if self.config.yaml_path and Path(self.config.yaml_path).exists():
            self._sources['yaml'] = YamlMetadataSource(self.config.yaml_path)
        
        # Add API source if configured
        if self.config.api_base_url:
            self._sources['api'] = ApiMetadataSource(
                base_url=self.config.api_base_url,
                auth_token=self.config.api_auth_token,
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
        # Check cache first
        cache_key = f"{source}:{key}" if source else key
        if cache_key in self._metadata_cache:
            return self._metadata_cache[cache_key]
        
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
        
        # Cache the result
        if value is not None:
            self._metadata_cache[cache_key] = value
            return value
        
        return default
    
    def get_required(self, key: str, source: Optional[str] = None) -> Any:
        """Get required metadata value, raise exception if not found"""
        value = self.get(key, source=source)
        if value is None:
            raise ValueError(f"Required metadata key '{key}' not found")
        return value
    
    def get_batch(self, keys: List[str], 
                  source: Optional[str] = None) -> Dict[str, Any]:
        """Fetch multiple keys at once"""
        return {key: self.get(key, source=source) for key in keys}
    
    def set(self, key: str, value: Any, source: str = 'env') -> None:
        """Set metadata value in cache (doesn't persist to source)"""
        cache_key = f"{source}:{key}"
        self._metadata_cache[cache_key] = value
    
    def refresh(self, source: Optional[str] = None) -> None:
        """Refresh metadata from sources"""
        if source:
            if source in self._sources:
                self._sources[source].refresh()
        else:
            for src in self._sources.values():
                src.refresh()
        
        # Clear cache after refresh
        self._metadata_cache.clear()
    
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


# Example usage
if __name__ == "__main__":
    # Configure metadata sources
    config = MetadataConfig(
        yaml_path="config/pipeline.yaml",
        api_base_url="https://metadata-api.azure.com",
        api_auth_token=os.environ.get("API_TOKEN"),
        env_prefix="DATAOFFLOAD_"
    )
    
    # Initialize metadata manager
    metadata = Metadata(config)
    
    # Get metadata from any source (searches all)
    db_name = metadata.get("database_name")
    
    # Get from specific source
    api_key = metadata.get("api_key", source="env")
    
    # Get required metadata (raises exception if not found)
    pipeline_name = metadata.get_required("pipeline.name")
    
    # Get multiple values at once
    batch_data = metadata.get_batch([
        "warehouse_host",
        "warehouse_port",
        "adls_container",
        "databricks_workspace"
    ])
    
    # Get all metadata from YAML source
    yaml_metadata = metadata.get_all(source="yaml")
    
    # Refresh metadata from all sources
    metadata.refresh()
    
    print(f"Database: {db_name}")
    print(f"Pipeline: {pipeline_name}")
    print(f"Available sources: {metadata.sources}")