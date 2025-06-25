import os
import logging
from datetime import datetime
from typing import Dict, Any, List
import json

from metadata import Metadata
from pipeline_task_system import (
    Pipeline, PipelineBuilder, PipelineType, Task, TaskResult, TaskStatus,
    ExportDataTask, UploadToADLSTask, DatabricksJobTask
)

logger = logging.getLogger(__name__)


# ============ Custom Task Examples ============

class DataQualityCheckTask(Task):
    """Custom task for data quality validation"""
    
    def validate(self) -> bool:
        """Validate configuration"""
        return self.metadata.get('data_quality.enabled', default=True, source='yaml')
    
    def execute(self, context: Dict[str, Any]) -> TaskResult:
        """Execute data quality checks"""
        start_time = datetime.now()
        
        try:
            # Get quality rules from metadata
            quality_rules = self.metadata.get('data_quality.rules', source='yaml') or []
            uploaded_paths = context.get('uploaded_paths', [])
            
            quality_results = []
            for path_info in uploaded_paths:
                table = path_info['table']
                
                # Simulate quality checks
                checks = {
                    'row_count': {'passed': True, 'value': 50000},
                    'null_checks': {'passed': True, 'critical_columns': 0},
                    'duplicate_checks': {'passed': True, 'duplicates': 0}
                }
                
                quality_results.append({
                    'table': table,
                    'checks': checks,
                    'overall_status': 'passed'
                })
                
                logger.info(f"Quality checks passed for table: {table}")
            
            return TaskResult(
                status=TaskStatus.SUCCESS,
                start_time=start_time,
                end_time=datetime.now(),
                output={'quality_results': quality_results},
                metadata={'rules_applied': len(quality_rules)}
            )
            
        except Exception as e:
            return TaskResult(
                status=TaskStatus.FAILED,
                start_time=start_time,
                end_time=datetime.now(),
                error=str(e)
            )


class NotificationTask(Task):
    """Task to send notifications"""
    
    def validate(self) -> bool:
        """Validate notification configuration"""
        return bool(self.metadata.get('monitoring.alert_email', source='yaml'))
    
    def execute(self, context: Dict[str, Any]) -> TaskResult:
        """Send notification"""
        start_time = datetime.now()
        
        try:
            email = self.metadata.get('monitoring.alert_email', source='yaml')
            notification_type = self.config.get('type', 'completion')
            
            # Build notification content based on context
            if notification_type == 'completion':
                subject = f"Pipeline '{context.get('pipeline_name', 'Unknown')}' completed"
                body = self._build_completion_report(context)
            elif notification_type == 'failure':
                subject = f"Pipeline '{context.get('pipeline_name', 'Unknown')}' failed"
                body = self._build_failure_report(context)
            else:
                subject = "Pipeline notification"
                body = json.dumps(context, indent=2)
            
            logger.info(f"Sending {notification_type} notification to {email}")
            logger.info(f"Subject: {subject}")
            
            # Here you would implement actual email sending
            # For now, we'll simulate it
            
            return TaskResult(
                status=TaskStatus.SUCCESS,
                start_time=start_time,
                end_time=datetime.now(),
                output={'notification_sent': True, 'recipient': email},
                metadata={'type': notification_type, 'subject': subject}
            )
            
        except Exception as e:
            return TaskResult(
                status=TaskStatus.FAILED,
                start_time=start_time,
                end_time=datetime.now(),
                error=str(e)
            )
    
    def _build_completion_report(self, context: Dict[str, Any]) -> str:
        """Build completion report"""
        report = ["Pipeline Execution Report", "=" * 50]
        
        if 'exported_files' in context:
            report.append("\nExported Files:")
            for file_info in context['exported_files']:
                report.append(f"  - {file_info['table']}: {file_info['rows']} rows")
        
        if 'quality_results' in context:
            report.append("\nData Quality Results:")
            for result in context['quality_results']:
                report.append(f"  - {result['table']}: {result['overall_status']}")
        
        return "\n".join(report)
    
    def _build_failure_report(self, context: Dict[str, Any]) -> str:
        """Build failure report"""
        return f"Pipeline failed at task: {context.get('failed_task', 'Unknown')}\n" \
               f"Error: {context.get('error', 'No error details available')}"


# ============ Usage Examples ============

def example_1_data_offloading_with_quality_checks():
    """Example: Data offloading pipeline with quality checks and notifications"""
    print("\n" + "="*60)
    print("Example 1: Data Offloading with Quality Checks")
    print("="*60)
    
    # Initialize metadata
    metadata = Metadata(environment_config_path="config/environments.json")
    
    # Create builder
    builder = PipelineBuilder(metadata)
    
    # Build pipeline with quality checks
    pipeline = (builder
        .create_pipeline("warehouse_to_adls_with_qa", PipelineType.DATA_OFFLOADING)
        .add_export_task()
        .add_upload_task()
        .add_custom_task(DataQualityCheckTask("quality_check", metadata))
        .add_databricks_task(job_type="unzip")
        .add_custom_task(NotificationTask("notify_completion", metadata, {'type': 'completion'}))
        .with_hook('before_pipeline', log_pipeline_start)
        .with_hook('after_task', log_task_completion)
        .with_hook('after_pipeline', log_pipeline_summary)
        .build()
    )
    
    # Add context
    pipeline.context['pipeline_name'] = pipeline.name
    
    # Execute
    if pipeline.validate():
        results = pipeline.execute()
        print_results(results)


def example_2_transformation_pipeline():
    """Example: Transformation pipeline with multiple Databricks jobs"""
    print("\n" + "="*60)
    print("Example 2: Data Transformation Pipeline")
    print("="*60)
    
    metadata = Metadata(environment_config_path="config/environments.json")
    builder = PipelineBuilder(metadata)
    
    # Custom transformation task
    class TransformationTask(DatabricksJobTask):
        def execute(self, context: Dict[str, Any]) -> TaskResult:
            # Custom logic for transformation
            self.config['transformation_type'] = context.get('transformation_type', 'default')
            return super().execute(context)
    
    # Build transformation pipeline
    pipeline = (builder
        .create_pipeline("customer_360_transform", PipelineType.TRANSFORMATION)
        .add_custom_task(TransformationTask(
            "aggregate_customer_data", 
            metadata, 
            {'job_type': 'customer_aggregation'}
        ))
        .add_custom_task(TransformationTask(
            "join_transaction_data", 
            metadata,
            {'job_type': 'transaction_join'}
        ))
        .add_custom_task(TransformationTask(
            "calculate_metrics",
            metadata,
            {'job_type': 'metric_calculation'}
        ))
        .add_custom_task(NotificationTask("notify_completion", metadata))
        .with_hook('after_task', track_transformation_metrics)
        .build()
    )
    
    # Set transformation context
    pipeline.context['transformation_type'] = 'customer_360'
    pipeline.context['target_tables'] = ['dim_customer', 'fact_transactions']
    
    if pipeline.validate():
        results = pipeline.execute()
        print_results(results)


def example_3_conditional_pipeline():
    """Example: Pipeline with conditional task execution"""
    print("\n" + "="*60)
    print("Example 3: Conditional Pipeline Execution")
    print("="*60)
    
    metadata = Metadata(environment_config_path="config/environments.json")
    
    # Custom conditional task
    class ConditionalTask(Task):
        def validate(self) -> bool:
            return True
        
        def execute(self, context: Dict[str, Any]) -> TaskResult:
            start_time = datetime.now()
            
            # Check condition from context
            should_execute = context.get(self.config.get('condition_key', 'execute'), True)
            
            if not should_execute:
                return TaskResult(
                    status=TaskStatus.SKIPPED,
                    start_time=start_time,
                    end_time=datetime.now(),
                    metadata={'reason': 'Condition not met'}
                )
            
            # Execute actual logic
            logger.info(f"Executing conditional task: {self.name}")
            
            return TaskResult(
                status=TaskStatus.SUCCESS,
                start_time=start_time,
                end_time=datetime.now(),
                output={'conditional_result': 'processed'}
            )
    
    # Build pipeline
    builder = PipelineBuilder(metadata)
    pipeline = (builder
        .create_pipeline("conditional_processing", PipelineType.CUSTOM)
        .add_export_task()
        .add_custom_task(ConditionalTask(
            "check_weekend_processing",
            metadata,
            {'condition_key': 'is_weekend'}
        ))
        .add_upload_task()
        .with_hook('before_pipeline', set_execution_context)
        .build()
    )
    
    # Set condition based on current day
    pipeline.context['is_weekend'] = datetime.now().weekday() >= 5
    
    if pipeline.validate():
        results = pipeline.execute()
        print_results(results)


def example_4_error_handling_pipeline():
    """Example: Pipeline with error handling and retry logic"""
    print("\n" + "="*60)
    print("Example 4: Pipeline with Error Handling")
    print("="*60)
    
    metadata = Metadata(environment_config_path="config/environments.json")
    
    # Task with retry logic
    class RetryableTask(Task):
        def validate(self) -> bool:
            return True
        
        def execute(self, context: Dict[str, Any]) -> TaskResult:
            start_time = datetime.now()
            max_retries = self.config.get('max_retries', 3)
            retry_count = context.get(f'{self.name}_retry_count', 0)
            
            try:
                # Simulate occasional failure
                if retry_count < 2:  # Fail first 2 attempts
                    raise Exception("Simulated failure for retry demo")
                
                return TaskResult(
                    status=TaskStatus.SUCCESS,
                    start_time=start_time,
                    end_time=datetime.now(),
                    output={'retry_count': retry_count}
                )
                
            except Exception as e:
                if retry_count < max_retries:
                    # Set retry flag in context
                    context[f'{self.name}_retry_count'] = retry_count + 1
                    context[f'{self.name}_should_retry'] = True
                    
                    return TaskResult(
                        status=TaskStatus.FAILED,
                        start_time=start_time,
                        end_time=datetime.now(),
                        error=f"{str(e)} (Retry {retry_count + 1}/{max_retries})"
                    )
                else:
                    return TaskResult(
                        status=TaskStatus.FAILED,
                        start_time=start_time,
                        end_time=datetime.now(),
                        error=f"{str(e)} (Max retries exceeded)"
                    )
    
    # Build pipeline with error handling
    builder = PipelineBuilder(metadata)
    pipeline = (builder
        .create_pipeline("resilient_pipeline", PipelineType.DATA_OFFLOADING)
        .add_export_task()
        .add_custom_task(RetryableTask("flaky_operation", metadata, {'max_retries': 3}))
        .add_upload_task()
        .with_hook('after_task', handle_task_failure)
        .with_hook('after_pipeline', send_failure_notification)
        .build()
    )
    
    if pipeline.validate():
        results = pipeline.execute()
        print_results(results)


# ============ Hook Functions ============

def log_pipeline_start(context: Dict[str, Any]):
    """Hook: Log pipeline start"""
    pipeline = context['pipeline']
    logger.info(f"{'='*60}")
    logger.info(f"Starting pipeline: {pipeline.name}")
    logger.info(f"Type: {pipeline.pipeline_type.value}")
    logger.info(f"Environment: {pipeline.metadata.current_environment}")
    logger.info(f"{'='*60}")


def log_task_completion(context: Dict[str, Any]):
    """Hook: Log task completion"""
    task = context['task']
    result = context['result']
    
    if result.status == TaskStatus.SUCCESS:
        logger.info(f"✓ Task '{task.name}' completed successfully")
    elif result.status == TaskStatus.FAILED:
        logger.error(f"✗ Task '{task.name}' failed: {result.error}")
    elif result.status == TaskStatus.SKIPPED:
        logger.warning(f"⚠ Task '{task.name}' was skipped")


def log_pipeline_summary(context: Dict[str, Any]):
    """Hook: Log pipeline summary"""
    pipeline = context['pipeline']
    results = context['results']
    
    success_count = sum(1 for r in results.values() if r.status == TaskStatus.SUCCESS)
    failed_count = sum(1 for r in results.values() if r.status == TaskStatus.FAILED)
    skipped_count = sum(1 for r in results.values() if r.status == TaskStatus.SKIPPED)
    
    logger.info(f"{'='*60}")
    logger.info(f"Pipeline Summary: {pipeline.name}")
    logger.info(f"  Successful: {success_count}")
    logger.info(f"  Failed: {failed_count}")
    logger.info(f"  Skipped: {skipped_count}")
    logger.info(f"{'='*60}")


def track_transformation_metrics(context: Dict[str, Any]):
    """Hook: Track transformation metrics"""
    task = context['task']
    result = context['result']
    
    if result.status == TaskStatus.SUCCESS and 'run_id' in result.output:
        # Here you would send metrics to monitoring system
        logger.info(f"Tracking metrics for transformation: {task.name}")
        logger.info(f"  Run ID: {result.output['run_id']}")
        logger.info(f"  Duration: {(result.end_time - result.start_time).total_seconds()}s")


def set_execution_context(context: Dict[str, Any]):
    """Hook: Set execution context based on environment"""
    pipeline = context['pipeline']
    
    # Add execution metadata
    pipeline.context['execution_time'] = datetime.now()
    pipeline.context['environment'] = pipeline.metadata.current_environment
    pipeline.context['triggered_by'] = 'scheduler'  # or could read from metadata


def handle_task_failure(context: Dict[str, Any]):
    """Hook: Handle task failure with retry logic"""
    task = context['task']
    result = context['result']
    
    if result.status == TaskStatus.FAILED:
        retry_flag = f'{task.name}_should_retry'
        if context.get('context', {}).get(retry_flag):
            logger.warning(f"Task '{task.name}' failed but will be retried")
            # Here you could implement actual retry logic
            # For demo, we'll just log it


def send_failure_notification(context: Dict[str, Any]):
    """Hook: Send notification on pipeline failure"""
    results = context['results']
    pipeline = context['pipeline']
    
    failed_tasks = [name for name, result in results.items() 
                    if result.status == TaskStatus.FAILED]
    
    if failed_tasks:
        logger.error(f"Pipeline '{pipeline.name}' failed")
        logger.error(f"Failed tasks: {', '.join(failed_tasks)}")
        # Here you would send actual notification


# ============ Helper Functions ============

def print_results(results: Dict[str, TaskResult]):
    """Pretty print pipeline results"""
    print("\nPipeline Execution Results:")
    print("-" * 40)
    for task_name, result in results.items():
        status_symbol = {
            TaskStatus.SUCCESS: "✓",
            TaskStatus.FAILED: "✗",
            TaskStatus.SKIPPED: "⚠"
        }.get(result.status, "?")
        
        print(f"{status_symbol} {task_name}: {result.status.value}")
        if result.error:
            print(f"  Error: {result.error}")
        if result.metadata:
            print(f"  Metadata: {result.metadata}")


# ============ Builder Pattern Explanation ============

def explain_builder_pattern():
    """
    Explanation of how the Builder Pattern works in Python
    
    The Builder Pattern with method chaining works through these key concepts:
    
    1. **Return self**: Each method returns 'self' (the instance itself)
    2. **Fluent Interface**: This creates a fluent interface for chaining
    3. **State Accumulation**: Each method modifies internal state
    4. **Final Build**: The build() method returns the constructed object
    """
    
    print("\n" + "="*60)
    print("Builder Pattern Explanation")
    print("="*60)
    
    # Simple example to demonstrate the pattern
    class SimpleBuilder:
        def __init__(self):
            self.data = {}
        
        def set_name(self, name: str) -> 'SimpleBuilder':
            self.data['name'] = name
            return self  # KEY: Return self for chaining
        
        def set_value(self, value: int) -> 'SimpleBuilder':
            self.data['value'] = value
            return self  # KEY: Return self for chaining
        
        def build(self) -> dict:
            return self.data
    
    # Usage
    result = (SimpleBuilder()
        .set_name("example")
        .set_value(42)
        .build()
    )
    
    print("Simple builder result:", result)
    
    # How it works step by step:
    print("\nStep-by-step execution:")
    print("1. SimpleBuilder() creates instance")
    print("2. .set_name('example') modifies instance and returns it")
    print("3. .set_value(42) modifies the SAME instance and returns it")
    print("4. .build() returns the final constructed data")
    
    # Benefits of Builder Pattern:
    print("\nBenefits of Builder Pattern:")
    print("- Readable and intuitive API")
    print("- Optional parameters without complex constructors")
    print("- Step-by-step object construction")
    print("- Validation can be done in build()")
    print("- Immutable objects can be created")


# ============ Main Execution ============

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Set up test environment
    os.environ['DSF_DOMAIN'] = 'D'
    os.environ['WAREHOUSE_HOST'] = 'localhost'
    os.environ['WAREHOUSE_USER'] = 'etl_user'
    os.environ['WAREHOUSE_PASSWORD'] = 'pass'
    os.environ['ADLS_ACCOUNT_NAME'] = 'storage'
    os.environ['ADLS_ACCOUNT_KEY'] = 'key'
    os.environ['DATABRICKS_TOKEN'] = 'token'
    
    # Run examples
    example_1_data_offloading_with_quality_checks()
    example_2_transformation_pipeline()
    example_3_conditional_pipeline()
    example_4_error_handling_pipeline()
    
    # Explain builder pattern
    explain_builder_pattern()