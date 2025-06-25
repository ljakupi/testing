from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Callable
from enum import Enum
from datetime import datetime
import logging
import json
from pathlib import Path

from metadata import Metadata

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


class PipelineType(Enum):
    """Types of pipelines"""
    DATA_OFFLOADING = "data_offloading"
    TRANSFORMATION = "transformation"
    CUSTOM = "custom"


@dataclass
class TaskResult:
    """Result of task execution"""
    status: TaskStatus
    start_time: datetime
    end_time: datetime
    output: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class Task(ABC):
    """Abstract base class for all tasks"""
    
    def __init__(self, name: str, metadata: Metadata, config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.metadata = metadata
        self.config = config or {}
        self.status = TaskStatus.PENDING
        self.result: Optional[TaskResult] = None
        self._dependencies: List['Task'] = []
        
    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> TaskResult:
        """Execute the task with given context"""
        pass
    
    @abstractmethod
    def validate(self) -> bool:
        """Validate task configuration before execution"""
        pass
    
    def add_dependency(self, task: 'Task') -> None:
        """Add a task that must complete before this one"""
        self._dependencies.append(task)
    
    def can_execute(self) -> bool:
        """Check if all dependencies are satisfied"""
        return all(dep.status == TaskStatus.SUCCESS for dep in self._dependencies)
    
    def get_required_metadata(self, key: str, source: Optional[str] = None) -> Any:
        """Helper to get required metadata with task context in error message"""
        try:
            return self.metadata.get_required(key, source)
        except ValueError as e:
            raise ValueError(f"Task '{self.name}': {str(e)}")


class ExportDataTask(Task):
    """Task to export data from warehouse to CSV files"""
    
    def validate(self) -> bool:
        """Validate database connection and table configuration"""
        required_keys = ['WAREHOUSE_HOST', 'WAREHOUSE_USER', 'WAREHOUSE_PASSWORD']
        for key in required_keys:
            if not self.metadata.get(key, source='env'):
                logger.error(f"Missing required environment variable: {key}")
                return False
        
        tables = self.metadata.get('warehouse.tables', source='yaml')
        if not tables:
            logger.error("No tables configured for export")
            return False
            
        return True
    
    def execute(self, context: Dict[str, Any]) -> TaskResult:
        """Execute data export"""
        start_time = datetime.now()
        
        try:
            # Get database configuration
            db_config = {
                'host': self.get_required_metadata('WAREHOUSE_HOST', source='env'),
                'port': self.metadata.get('WAREHOUSE_PORT', default=5432, source='env'),
                'database': self.get_required_metadata('warehouse.database_name', source='yaml'),
                'user': self.get_required_metadata('WAREHOUSE_USER', source='env'),
                'password': self.get_required_metadata('WAREHOUSE_PASSWORD', source='env')
            }
            
            # Get export configuration
            batch_size = self.metadata.get('offload.batch_size', default=100000, source='yaml')
            compression = self.metadata.get('offload.compression', default='gzip', source='yaml')
            tables = self.metadata.get('warehouse.tables', source='yaml')
            
            exported_files = []
            
            for table_config in tables:
                table_name = table_config.get('name')
                partition_column = table_config.get('partition_column')
                
                logger.info(f"Exporting table: {table_name}")
                
                # Here you would implement actual database export logic
                # For now, we'll simulate the export
                output_file = f"/tmp/{table_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv.gz"
                exported_files.append({
                    'table': table_name,
                    'file': output_file,
                    'rows': 50000,  # Simulated
                    'size_mb': 25.5  # Simulated
                })
                
                logger.info(f"Exported {table_name} to {output_file}")
            
            return TaskResult(
                status=TaskStatus.SUCCESS,
                start_time=start_time,
                end_time=datetime.now(),
                output={'exported_files': exported_files},
                metadata={'batch_size': batch_size, 'compression': compression}
            )
            
        except Exception as e:
            logger.error(f"Export failed: {str(e)}")
            return TaskResult(
                status=TaskStatus.FAILED,
                start_time=start_time,
                end_time=datetime.now(),
                error=str(e)
            )


class UploadToADLSTask(Task):
    """Task to upload files to Azure Data Lake Storage"""
    
    def validate(self) -> bool:
        """Validate ADLS configuration"""
        required = ['azure.adls.container', 'ADLS_ACCOUNT_NAME', 'ADLS_ACCOUNT_KEY']
        
        for key in required:
            source = 'yaml' if key.startswith('azure.') else 'env'
            if not self.metadata.get(key, source=source):
                logger.error(f"Missing required configuration: {key}")
                return False
                
        return True
    
    def execute(self, context: Dict[str, Any]) -> TaskResult:
        """Execute file upload to ADLS"""
        start_time = datetime.now()
        
        try:
            # Get ADLS configuration
            container = self.get_required_metadata('azure.adls.container', source='yaml')
            account_name = self.get_required_metadata('ADLS_ACCOUNT_NAME', source='env')
            account_key = self.get_required_metadata('ADLS_ACCOUNT_KEY', source='env')
            path_pattern = self.metadata.get('azure.adls.path_pattern', source='yaml')
            
            # Get files from previous task
            exported_files = context.get('exported_files', [])
            if not exported_files:
                raise ValueError("No files to upload from previous task")
            
            uploaded_paths = []
            
            for file_info in exported_files:
                table_name = file_info['table']
                local_file = file_info['file']
                
                # Generate ADLS path
                adls_path = self._generate_adls_path(path_pattern, table_name)
                
                logger.info(f"Uploading {local_file} to {adls_path}")
                
                # Here you would implement actual ADLS upload logic
                # For now, we'll simulate the upload
                uploaded_paths.append({
                    'table': table_name,
                    'adls_path': adls_path,
                    'size_mb': file_info['size_mb']
                })
                
                logger.info(f"Successfully uploaded to {adls_path}")
            
            return TaskResult(
                status=TaskStatus.SUCCESS,
                start_time=start_time,
                end_time=datetime.now(),
                output={'uploaded_paths': uploaded_paths},
                metadata={'container': container, 'total_files': len(uploaded_paths)}
            )
            
        except Exception as e:
            logger.error(f"Upload failed: {str(e)}")
            return TaskResult(
                status=TaskStatus.FAILED,
                start_time=start_time,
                end_time=datetime.now(),
                error=str(e)
            )
    
    def _generate_adls_path(self, pattern: str, table_name: str) -> str:
        """Generate ADLS path based on pattern"""
        database = self.metadata.get('warehouse.database_name', source='yaml')
        schema = self.metadata.get('warehouse.schema', default='public', source='yaml')
        date = datetime.now().strftime('%Y-%m-%d')
        
        return pattern.format(
            database=database,
            schema=schema,
            table=table_name,
            date=date
        )


class DatabricksJobTask(Task):
    """Task to trigger Databricks job"""
    
    def validate(self) -> bool:
        """Validate Databricks configuration"""
        required = ['azure.databricks.workspace_url', 'DATABRICKS_TOKEN']
        
        for key in required:
            source = 'yaml' if key.startswith('azure.') else 'env'
            if not self.metadata.get(key, source=source):
                logger.error(f"Missing required configuration: {key}")
                return False
                
        return True
    
    def execute(self, context: Dict[str, Any]) -> TaskResult:
        """Execute Databricks job"""
        start_time = datetime.now()
        
        try:
            # Get Databricks configuration
            workspace_url = self.get_required_metadata('azure.databricks.workspace_url', source='yaml')
            token = self.get_required_metadata('DATABRICKS_TOKEN', source='env')
            
            # Get job ID based on task configuration
            job_type = self.config.get('job_type', 'unzip')
            job_id_key = f'azure.databricks.job_configs.{job_type}_job_id'
            job_id = self.get_required_metadata(job_id_key, source='yaml')
            
            # Get uploaded paths from previous task
            uploaded_paths = context.get('uploaded_paths', [])
            
            # Prepare job parameters
            job_params = {
                'files': [path['adls_path'] for path in uploaded_paths],
                'output_format': self.metadata.get('azure.adls.file_format', default='parquet', source='yaml')
            }
            
            logger.info(f"Triggering Databricks job {job_id} with params: {job_params}")
            
            # Here you would implement actual Databricks API call
            # For now, we'll simulate the job execution
            run_id = f"run_{job_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            return TaskResult(
                status=TaskStatus.SUCCESS,
                start_time=start_time,
                end_time=datetime.now(),
                output={'run_id': run_id, 'job_id': job_id},
                metadata={'workspace': workspace_url, 'job_type': job_type}
            )
            
        except Exception as e:
            logger.error(f"Databricks job failed: {str(e)}")
            return TaskResult(
                status=TaskStatus.FAILED,
                start_time=start_time,
                end_time=datetime.now(),
                error=str(e)
            )


class Pipeline:
    """Pipeline orchestrator for executing tasks"""
    
    def __init__(self, name: str, pipeline_type: PipelineType, metadata: Metadata):
        self.name = name
        self.pipeline_type = pipeline_type
        self.metadata = metadata
        self.tasks: List[Task] = []
        self.context: Dict[str, Any] = {}
        self.results: Dict[str, TaskResult] = {}
        self._hooks: Dict[str, List[Callable]] = {
            'before_pipeline': [],
            'after_pipeline': [],
            'before_task': [],
            'after_task': []
        }
    
    def add_task(self, task: Task) -> 'Pipeline':
        """Add task to pipeline"""
        self.tasks.append(task)
        return self
    
    def add_hook(self, event: str, hook: Callable) -> 'Pipeline':
        """Add lifecycle hook"""
        if event in self._hooks:
            self._hooks[event].append(hook)
        return self
    
    def validate(self) -> bool:
        """Validate all tasks in pipeline"""
        logger.info(f"Validating pipeline: {self.name}")
        
        for task in self.tasks:
            if not task.validate():
                logger.error(f"Task validation failed: {task.name}")
                return False
                
        logger.info("Pipeline validation successful")
        return True
    
    def execute(self) -> Dict[str, TaskResult]:
        """Execute all tasks in pipeline"""
        logger.info(f"Starting pipeline: {self.name}")
        pipeline_start = datetime.now()
        
        # Execute before_pipeline hooks
        self._execute_hooks('before_pipeline', {'pipeline': self})
        
        try:
            for task in self.tasks:
                # Check dependencies
                if not task.can_execute():
                    logger.error(f"Task dependencies not satisfied: {task.name}")
                    task.result = TaskResult(
                        status=TaskStatus.SKIPPED,
                        start_time=datetime.now(),
                        end_time=datetime.now(),
                        error="Dependencies not satisfied"
                    )
                    self.results[task.name] = task.result
                    continue
                
                # Execute before_task hooks
                self._execute_hooks('before_task', {'task': task, 'context': self.context})
                
                logger.info(f"Executing task: {task.name}")
                task.status = TaskStatus.RUNNING
                
                # Execute task
                result = task.execute(self.context)
                task.status = result.status
                task.result = result
                self.results[task.name] = result
                
                # Update context with task output
                if result.status == TaskStatus.SUCCESS and result.output:
                    self.context.update(result.output)
                
                # Execute after_task hooks
                self._execute_hooks('after_task', {'task': task, 'result': result})
                
                # Stop pipeline if task failed
                if result.status == TaskStatus.FAILED:
                    logger.error(f"Pipeline stopped due to task failure: {task.name}")
                    break
            
            pipeline_end = datetime.now()
            duration = (pipeline_end - pipeline_start).total_seconds()
            logger.info(f"Pipeline completed in {duration:.2f} seconds")
            
        finally:
            # Execute after_pipeline hooks
            self._execute_hooks('after_pipeline', {'pipeline': self, 'results': self.results})
        
        return self.results
    
    def _execute_hooks(self, event: str, context: Dict[str, Any]) -> None:
        """Execute hooks for given event"""
        for hook in self._hooks[event]:
            try:
                hook(context)
            except Exception as e:
                logger.error(f"Hook execution failed for {event}: {str(e)}")


class PipelineBuilder:
    """Builder pattern for constructing pipelines"""
    
    def __init__(self, metadata: Metadata):
        self.metadata = metadata
        self._pipeline: Optional[Pipeline] = None
    
    def create_pipeline(self, name: str, pipeline_type: PipelineType) -> 'PipelineBuilder':
        """Create new pipeline"""
        self._pipeline = Pipeline(name, pipeline_type, self.metadata)
        return self
    
    def add_export_task(self, name: str = "export_data", config: Optional[Dict[str, Any]] = None) -> 'PipelineBuilder':
        """Add data export task"""
        if not self._pipeline:
            raise ValueError("Pipeline not created. Call create_pipeline first.")
        
        task = ExportDataTask(name, self.metadata, config)
        self._pipeline.add_task(task)
        return self
    
    def add_upload_task(self, name: str = "upload_to_adls", config: Optional[Dict[str, Any]] = None) -> 'PipelineBuilder':
        """Add ADLS upload task"""
        if not self._pipeline:
            raise ValueError("Pipeline not created. Call create_pipeline first.")
        
        task = UploadToADLSTask(name, self.metadata, config)
        
        # Add dependency on export task if it exists
        export_tasks = [t for t in self._pipeline.tasks if isinstance(t, ExportDataTask)]
        if export_tasks:
            task.add_dependency(export_tasks[-1])
        
        self._pipeline.add_task(task)
        return self
    
    def add_databricks_task(self, name: str = "databricks_job", job_type: str = "unzip", 
                           config: Optional[Dict[str, Any]] = None) -> 'PipelineBuilder':
        """Add Databricks job task"""
        if not self._pipeline:
            raise ValueError("Pipeline not created. Call create_pipeline first.")
        
        task_config = config or {}
        task_config['job_type'] = job_type
        
        task = DatabricksJobTask(name, self.metadata, task_config)
        
        # Add dependency on upload task if it exists
        upload_tasks = [t for t in self._pipeline.tasks if isinstance(t, UploadToADLSTask)]
        if upload_tasks:
            task.add_dependency(upload_tasks[-1])
        
        self._pipeline.add_task(task)
        return self
    
    def add_custom_task(self, task: Task) -> 'PipelineBuilder':
        """Add custom task"""
        if not self._pipeline:
            raise ValueError("Pipeline not created. Call create_pipeline first.")
        
        self._pipeline.add_task(task)
        return self
    
    def with_hook(self, event: str, hook: Callable) -> 'PipelineBuilder':
        """Add lifecycle hook"""
        if not self._pipeline:
            raise ValueError("Pipeline not created. Call create_pipeline first.")
        
        self._pipeline.add_hook(event, hook)
        return self
    
    def build(self) -> Pipeline:
        """Build and return pipeline"""
        if not self._pipeline:
            raise ValueError("Pipeline not created. Call create_pipeline first.")
        
        return self._pipeline


# Example usage
if __name__ == "__main__":
    import os
    
    # Set up environment
    os.environ['DSF_DOMAIN'] = 'D'  # Development
    os.environ['WAREHOUSE_HOST'] = 'localhost'
    os.environ['WAREHOUSE_USER'] = 'etl_user'
    os.environ['WAREHOUSE_PASSWORD'] = 'secure_pass'
    os.environ['ADLS_ACCOUNT_NAME'] = 'mystorageaccount'
    os.environ['ADLS_ACCOUNT_KEY'] = 'storage_key'
    os.environ['DATABRICKS_TOKEN'] = 'databricks_token'
    
    # Initialize metadata
    metadata = Metadata(environment_config_path="config/environments.json")
    
    # Build data offloading pipeline using builder pattern
    builder = PipelineBuilder(metadata)
    
    offloading_pipeline = (builder
        .create_pipeline("warehouse_to_adls", PipelineType.DATA_OFFLOADING)
        .add_export_task()
        .add_upload_task()
        .add_databricks_task(job_type="unzip")
        .with_hook('after_task', lambda ctx: logger.info(f"Task {ctx['task'].name} completed"))
        .build()
    )
    
    # Validate pipeline
    if offloading_pipeline.validate():
        # Execute pipeline
        results = offloading_pipeline.execute()
        
        # Print results
        print("\nPipeline Results:")
        for task_name, result in results.items():
            print(f"  {task_name}: {result.status.value}")
            if result.error:
                print(f"    Error: {result.error}")
    
    # Example of creating a transformation pipeline
    transformation_pipeline = (builder
        .create_pipeline("data_transformation", PipelineType.TRANSFORMATION)
        .add_databricks_task(name="join_tables", job_type="transform")
        .build()
    )