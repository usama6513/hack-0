"""
Audit Logger Skill for AI Employee - Gold Tier
Implements comprehensive audit logging for all operations.
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('audit_logger.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AuditLogger:
    """
    Skill to provide comprehensive audit logging for all AI Employee operations.
    """

    def __init__(self, vault_path="./"):
        self.vault_path = vault_path
        self.audit_dir = os.path.join(vault_path, "Audit_Logs")
        self.operations_dir = os.path.join(self.audit_dir, "Operations")
        self.security_dir = os.path.join(self.audit_dir, "Security")
        self.compliance_dir = os.path.join(self.audit_dir, "Compliance")
        self.config_dir = os.path.join(vault_path, "Config")
        self.audit_config_file = os.path.join(self.config_dir, "audit_config.json")

        # Ensure directories exist
        os.makedirs(self.audit_dir, exist_ok=True)
        os.makedirs(self.operations_dir, exist_ok=True)
        os.makedirs(self.security_dir, exist_ok=True)
        os.makedirs(self.compliance_dir, exist_ok=True)
        os.makedirs(self.config_dir, exist_ok=True)

        # Load audit configuration
        self.audit_config = self._load_audit_config()

    def _load_audit_config(self) -> Dict[str, Any]:
        """Load audit configuration."""
        if os.path.exists(self.audit_config_file):
            with open(self.audit_config_file, 'r') as f:
                return json.load(f)
        else:
            # Create default audit configuration
            default_config = {
                "log_levels": {
                    "operations": "INFO",
                    "security": "WARNING",
                    "compliance": "INFO"
                },
                "retention_days": {
                    "operations": 90,
                    "security": 365,
                    "compliance": 730
                },
                "enabled_logs": {
                    "operations": True,
                    "security": True,
                    "compliance": True
                },
                "audit_categories": [
                    "user_authentication",
                    "data_access",
                    "system_configuration",
                    "communication",
                    "social_media_posting",
                    "accounting_operations",
                    "scheduled_tasks",
                    "error_events",
                    "recovery_operations"
                ]
            }
            with open(self.audit_config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            logger.info(f"[OK] Created default audit configuration: {self.audit_config_file}")
            return default_config

    def log_operation(self, operation_type: str, details: Dict[str, Any], severity: str = "INFO") -> str:
        """Log an operation with comprehensive details."""
        if not self.audit_config["enabled_logs"].get("operations", False):
            return None

        # Create audit entry
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "operation_type": operation_type,
            "details": details,
            "severity": severity,
            "session_id": details.get("session_id") or "unknown",
            "user_id": details.get("user_id") or "system",
            "source_component": details.get("source_component") or "unknown",
            "correlation_id": details.get("correlation_id") or "none"
        }

        # Determine log file based on operation type
        log_file = os.path.join(self.operations_dir, f"operations_{datetime.now().strftime('%Y%m%d')}.jsonl")

        # Append to log file
        with open(log_file, 'a') as f:
            f.write(json.dumps(audit_entry) + '\n')

        logger.info(f"[OK] Operation logged: {operation_type} - {log_file}")
        return log_file

    def log_security_event(self, event_type: str, details: Dict[str, Any]) -> str:
        """Log a security event."""
        if not self.audit_config["enabled_logs"].get("security", False):
            return None

        security_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "details": details,
            "severity": "WARNING" if event_type in ["failed_login", "unauthorized_access"] else "INFO",
            "user_id": details.get("user_id") or "unknown",
            "source_ip": details.get("source_ip") or "local",
            "action_taken": details.get("action_taken") or "logged"
        }

        log_file = os.path.join(self.security_dir, f"security_{datetime.now().strftime('%Y%m%d')}.jsonl")

        with open(log_file, 'a') as f:
            f.write(json.dumps(security_entry) + '\n')

        logger.info(f"[OK] Security event logged: {event_type} - {log_file}")
        return log_file

    def log_compliance_data(self, compliance_type: str, details: Dict[str, Any]) -> str:
        """Log compliance-related data."""
        if not self.audit_config["enabled_logs"].get("compliance", False):
            return None

        compliance_entry = {
            "timestamp": datetime.now().isoformat(),
            "compliance_type": compliance_type,
            "details": details,
            "status": "logged",
            "review_required": details.get("review_required", False),
            "data_retention_compliant": True
        }

        log_file = os.path.join(self.compliance_dir, f"compliance_{datetime.now().strftime('%Y%m%d')}.jsonl")

        with open(log_file, 'a') as f:
            f.write(json.dumps(compliance_entry) + '\n')

        logger.info(f"[OK] Compliance data logged: {compliance_type} - {log_file}")
        return log_file

    def log_user_authentication(self, user_id: str, action: str, details: Dict[str, Any] = None) -> str:
        """Log user authentication events."""
        auth_details = {
            "user_id": user_id,
            "action": action,
            "timestamp": datetime.now().isoformat(),
            "source_component": "authentication",
            "details": details or {}
        }

        return self.log_operation("user_authentication", auth_details)

    def log_data_access(self, user_id: str, data_type: str, action: str, details: Dict[str, Any] = None) -> str:
        """Log data access events."""
        access_details = {
            "user_id": user_id,
            "data_type": data_type,
            "action": action,
            "timestamp": datetime.now().isoformat(),
            "source_component": "data_access",
            "details": details or {}
        }

        return self.log_operation("data_access", access_details)

    def log_social_media_action(self, platform: str, action: str, details: Dict[str, Any] = None) -> str:
        """Log social media actions."""
        sm_details = {
            "platform": platform,
            "action": action,
            "timestamp": datetime.now().isoformat(),
            "source_component": "social_media",
            "details": details or {}
        }

        return self.log_operation("social_media_action", sm_details)

    def log_accounting_operation(self, operation: str, details: Dict[str, Any] = None) -> str:
        """Log accounting operations."""
        acc_details = {
            "operation": operation,
            "timestamp": datetime.now().isoformat(),
            "source_component": "accounting",
            "details": details or {}
        }

        return self.log_operation("accounting_operation", acc_details)

    def generate_audit_summary(self, days: int = 7) -> Dict[str, Any]:
        """Generate audit summary for the specified number of days."""
        summary = {
            "period": f"Last {days} days",
            "start_date": (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d'),
            "end_date": datetime.now().strftime('%Y-%m-%d'),
            "operations": self._count_operation_logs(days),
            "security_events": self._count_security_logs(days),
            "compliance_records": self._count_compliance_logs(days),
            "generated_at": datetime.now().isoformat()
        }

        summary_file = os.path.join(self.audit_dir, f"audit_summary_{datetime.now().strftime('%Y%m%d')}.json")
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)

        logger.info(f"[OK] Audit summary generated: {summary_file}")
        return summary

    def _count_operation_logs(self, days: int) -> Dict[str, int]:
        """Count operation logs for the specified number of days."""
        import glob
        from datetime import timedelta

        counts = {}
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y%m%d')
            pattern = os.path.join(self.operations_dir, f"operations_{date}.jsonl")
            files = glob.glob(pattern)

            total_entries = 0
            for file in files:
                with open(file, 'r') as f:
                    total_entries += sum(1 for line in f)

            counts[date] = total_entries

        return counts

    def _count_security_logs(self, days: int) -> Dict[str, int]:
        """Count security logs for the specified number of days."""
        import glob
        from datetime import timedelta

        counts = {}
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y%m%d')
            pattern = os.path.join(self.security_dir, f"security_{date}.jsonl")
            files = glob.glob(pattern)

            total_entries = 0
            for file in files:
                with open(file, 'r') as f:
                    total_entries += sum(1 for line in f)

            counts[date] = total_entries

        return counts

    def _count_compliance_logs(self, days: int) -> Dict[str, int]:
        """Count compliance logs for the specified number of days."""
        import glob
        from datetime import timedelta

        counts = {}
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y%m%d')
            pattern = os.path.join(self.compliance_dir, f"compliance_{date}.jsonl")
            files = glob.glob(pattern)

            total_entries = 0
            for file in files:
                with open(file, 'r') as f:
                    total_entries += sum(1 for line in f)

            counts[date] = total_entries

        return counts

    def run_log_cleanup(self) -> Dict[str, int]:
        """Clean up old log files based on retention policies."""
        import glob
        from datetime import datetime, timedelta

        cleanup_stats = {"operations": 0, "security": 0, "compliance": 0}

        # Clean up operation logs
        retention_days = self.audit_config["retention_days"]["operations"]
        cutoff_date = datetime.now() - timedelta(days=retention_days)

        for dir_path, log_type in [(self.operations_dir, "operations"), (self.security_dir, "security"), (self.compliance_dir, "compliance")]:
            all_files = glob.glob(os.path.join(dir_path, "*.jsonl"))

            for file_path in all_files:
                # Extract date from filename (format: prefix_YYYYMMDD.jsonl)
                filename = os.path.basename(file_path)
                date_str = filename.split('_')[-1].split('.')[0]  # Get the date part

                try:
                    file_date = datetime.strptime(date_str, '%Y%m%d')
                    if file_date < cutoff_date:
                        os.remove(file_path)
                        cleanup_stats[log_type] += 1
                except ValueError:
                    # If we can't parse the date, keep the file
                    continue

        logger.info(f"[OK] Log cleanup completed: {cleanup_stats}")
        return cleanup_stats

    def get_audit_trail(self, category: str, start_date: str = None, end_date: str = None) -> List[Dict[str, Any]]:
        """Get audit trail for a specific category within date range."""
        import glob

        if category == "operations":
            log_dir = self.operations_dir
        elif category == "security":
            log_dir = self.security_dir
        elif category == "compliance":
            log_dir = self.compliance_dir
        else:
            logger.error(f"[ERROR] Unknown audit category: {category}")
            return []

        # Find all log files in the directory
        pattern = os.path.join(log_dir, f"{category}_*.jsonl")
        log_files = glob.glob(pattern)

        trail = []
        for file_path in log_files:
            with open(file_path, 'r') as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        # Filter by date if specified
                        if start_date and end_date:
                            entry_date = datetime.fromisoformat(entry["timestamp"].replace('Z', '+00:00')).strftime('%Y-%m-%d')
                            if not (start_date <= entry_date <= end_date):
                                continue
                        trail.append(entry)
                    except:
                        continue

        # Sort by timestamp
        trail.sort(key=lambda x: x["timestamp"])
        return trail

    def run_single_check(self):
        """Run single check for audit logging."""
        logger.info("Running audit logging check...")

        # Generate summary
        summary = self.generate_audit_summary(7)

        # Run cleanup
        cleanup_stats = self.run_log_cleanup()

        logger.info(f"[OK] Audit logging check completed. Summary: {len(summary)} items, Cleanup: {sum(cleanup_stats.values())} files")
        return True

if __name__ == "__main__":
    from datetime import timedelta
    import glob

    # For testing
    audit_logger = AuditLogger()

    # Test logging various operations
    audit_logger.log_operation("test_operation", {
        "user_id": "system",
        "session_id": "test_session_123",
        "source_component": "test_module",
        "details": {"test_param": "test_value"}
    })

    audit_logger.log_security_event("test_event", {
        "user_id": "system",
        "source_ip": "127.0.0.1",
        "details": {"event_description": "Test security event"}
    })

    audit_logger.log_compliance_data("test_compliance", {
        "review_required": False,
        "details": {"compliance_check": "test_passed"}
    })

    # Generate summary
    summary = audit_logger.generate_audit_summary(1)
    print(f"[OK] Audit summary generated: {summary}")

    # Run a check
    audit_logger.run_single_check()
    print("[OK] Audit logging check completed successfully")