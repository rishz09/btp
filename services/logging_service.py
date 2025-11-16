"""
Logging Service - Microservice for structured logging and monitoring
Implements: Observability, Debugging, Audit trails
"""
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path


class LoggingService:
    """
    Maintainability: Structured logging for debugging
    Dependability: Audit trail for system behavior
    """
    
    def __init__(self, log_dir: str = "logs", config: dict = None):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.config = config or {}
        self.log_level = self.config.get('monitoring', {}).get('log_level', 'INFO')
        
        # Create separate log files for different components
        self.workflow_log = self.log_dir / "workflows.jsonl"
        self.metrics_log = self.log_dir / "metrics.jsonl"
        self.errors_log = self.log_dir / "errors.jsonl"
        self.system_log = self.log_dir / "system.log"
    
    def log_workflow(self, workflow_result: Dict[str, Any]):
        """Log workflow execution details"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': 'workflow',
            'workflow_id': workflow_result.get('workflow_id'),
            'status': workflow_result.get('status'),
            'stages_completed': workflow_result.get('metrics', {}).get('stages_completed', 0),
            'total_latency_ms': workflow_result.get('metrics', {}).get('total_latency_ms', 0),
            'total_tokens': workflow_result.get('metrics', {}).get('total_tokens', 0)
        }
        
        self._append_json_log(self.workflow_log, log_entry)
    
    def log_metrics(self, metrics: Dict[str, Any]):
        """Log evaluation metrics"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': 'metrics',
            **metrics
        }
        
        self._append_json_log(self.metrics_log, log_entry)
    
    def log_error(self, error: Exception, context: Dict[str, Any] = None):
        """Log errors with context"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': 'error',
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context or {}
        }
        
        self._append_json_log(self.errors_log, log_entry)
    
    def log_system(self, level: str, message: str, data: Dict[str, Any] = None):
        """Log system messages"""
        if not self._should_log(level):
            return
        
        timestamp = datetime.now().isoformat()
        log_line = f"[{timestamp}] [{level}] {message}"
        
        if data:
            log_line += f" | Data: {json.dumps(data)}"
        
        log_line += "\n"
        
        with open(self.system_log, 'a') as f:
            f.write(log_line)
    
    # def _append_json_log(self, log_file: Path, entry: Dict[str, Any]):
    #     """Append JSON log entry (JSONL format)"""
    #     with open(log_file, 'a') as f:
    #         f.write(json.dumps(entry) + '\n')
    
    def _append_json_log(self, log_file: Path, entry: Dict[str, Any]):
        """Append JSON log entry (JSONL format) and convert non-JSON types"""
        def default(o):
            if isinstance(o, datetime):
                return o.isoformat()
            return str(o)

        with open(log_file, 'a') as f:
            f.write(json.dumps(entry, default=default) + '\n')


    def _should_log(self, level: str) -> bool:
        """Check if message should be logged based on log level"""
        levels = {'DEBUG': 0, 'INFO': 1, 'WARNING': 2, 'ERROR': 3}
        return levels.get(level, 0) >= levels.get(self.log_level, 1)
    
    def get_recent_workflows(self, n: int = 10) -> list:
        """Retrieve recent workflow logs"""
        if not self.workflow_log.exists():
            return []
        
        with open(self.workflow_log, 'r') as f:
            lines = f.readlines()
            return [json.loads(line) for line in lines[-n:]]
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of errors"""
        if not self.errors_log.exists():
            return {'total_errors': 0}
        
        with open(self.errors_log, 'r') as f:
            errors = [json.loads(line) for line in f.readlines()]
        
        error_types = {}
        for error in errors:
            error_type = error.get('error_type', 'Unknown')
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        return {
            'total_errors': len(errors),
            'error_types': error_types,
            'recent_errors': errors[-5:] if errors else []
        }