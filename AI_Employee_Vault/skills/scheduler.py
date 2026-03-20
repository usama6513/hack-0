"""
Scheduler Skill for AI Employee - Silver Tier
Manages automated scheduling of tasks using cron-like functionality.
"""

import os
import json
import logging
import schedule
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from croniter import croniter

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class Scheduler:
    """
    Scheduler for AI Employee tasks using schedule library and cron expressions.
    """

    def __init__(self, vault_path="./"):
        self.vault_path = vault_path
        self.schedules_dir = os.path.join(vault_path, "Schedules")
        self.logs_dir = os.path.join(vault_path, "Scheduler_Logs")
        self.config_path = os.path.join(vault_path, "scheduler_config.json")

        # Ensure directories exist
        for directory in [self.schedules_dir, self.logs_dir]:
            os.makedirs(directory, exist_ok=True)

        # Load configuration
        self.config = self.load_config()

        # Scheduled jobs storage
        self.jobs = {}
        self.job_counter = 0

        # Running flag
        self.running = False

    def load_config(self) -> Dict:
        """Load scheduler configuration."""
        default_config = {
            "timezone": "UTC",
            "max_concurrent_jobs": 5,
            "retry_failed_jobs": True,
            "max_retries": 3,
            "default_schedule": {
                "gmail_check": "*/5 * * * *",      # Every 5 minutes
                "whatsapp_check": "*/2 * * * *",   # Every 2 minutes
                "linkedin_check": "*/10 * * * *",  # Every 10 minutes
                "linkedin_post": "0 9 * * 1-5",    # Weekdays at 9 AM
                "backup_vault": "0 2 * * *",       # Daily at 2 AM
                "cleanup_logs": "0 3 * * 0"        # Weekly on Sunday at 3 AM
            },
            "enabled_tasks": {
                "gmail_watcher": True,
                "whatsapp_watcher": True,
                "linkedin_watcher": True,
                "linkedin_poster": True,
                "email_sender": True,
                "approval_workflow": True
            }
        }

        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
            except Exception as e:
                logger.error(f"Error loading scheduler config: {e}")
                return default_config
        else:
            # Create default config
            try:
                with open(self.config_path, 'w') as f:
                    json.dump(default_config, f, indent=2)
                logger.info(f"Created default scheduler config at {self.config_path}")
            except Exception as e:
                logger.error(f"Error creating scheduler config: {e}")
            return default_config

    def schedule_task(self, task_name: str, schedule_expr: str, task_func, *args, **kwargs) -> str:
        """Schedule a task with cron expression."""
        job_id = f"{task_name}_{self.job_counter}"
        self.job_counter += 1

        try:
            # Parse cron expression
            cron = croniter(schedule_expr)
            next_run = cron.get_next(datetime)

            # Create job
            job = {
                "id": job_id,
                "name": task_name,
                "schedule": schedule_expr,
                "function": task_func,
                "args": args,
                "kwargs": kwargs,
                "next_run": next_run,
                "last_run": None,
                "run_count": 0,
                "error_count": 0,
                "enabled": True
            }

            self.jobs[job_id] = job
            self.save_job_schedule(job)

            logger.info(f"Scheduled task '{task_name}' with ID: {job_id}")
            logger.info(f"Next run: {next_run}")

            return job_id

        except Exception as e:
            logger.error(f"Error scheduling task '{task_name}': {e}")
            return None

    def save_job_schedule(self, job: Dict):
        """Save job schedule to file."""
        schedule_file = os.path.join(self.schedules_dir, f"{job['id']}.json")
        try:
            with open(schedule_file, 'w') as f:
                # Remove function object before saving
                job_copy = job.copy()
                job_copy['function'] = job_copy['function'].__name__
                json.dump(job_copy, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving job schedule: {e}")

    def load_job_schedules(self):
        """Load saved job schedules."""
        for filename in os.listdir(self.schedules_dir):
            if filename.endswith('.json'):
                try:
                    with open(os.path.join(self.schedules_dir, filename), 'r') as f:
                        job_data = json.load(f)
                        # Note: Function references need to be restored
                        logger.info(f"Loaded job schedule: {job_data['id']}")
                except Exception as e:
                    logger.error(f"Error loading job schedule {filename}: {e}")

    def run_scheduled_task(self, job_id: str):
        """Execute a scheduled task."""
        job = self.jobs.get(job_id)
        if not job or not job["enabled"]:
            return

        try:
            logger.info(f"Running scheduled task: {job['name']} (ID: {job_id})")

            # Execute task
            start_time = datetime.now()
            result = job["function"](*job["args"], **job["kwargs"])
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            # Update job stats
            job["last_run"] = start_time.isoformat()
            job["run_count"] += 1

            # Log success
            self.log_task_execution(job, True, duration, result)

            # Update next run time
            cron = croniter(job["schedule"])
            job["next_run"] = cron.get_next(datetime)

            logger.info(f"Task completed successfully in {duration:.2f} seconds")

        except Exception as e:
            logger.error(f"Error running scheduled task {job_id}: {e}")
            job["error_count"] += 1
            self.log_task_execution(job, False, 0, str(e))

            # Retry logic
            if self.config.get("retry_failed_jobs", False) and job["error_count"] < self.config.get("max_retries", 3):
                logger.info(f"Will retry task {job_id} (attempt {job['error_count'] + 1})")
            else:
                logger.error(f"Task {job_id} failed permanently after {job['error_count']} attempts")

    def log_task_execution(self, job: Dict, success: bool, duration: float, result):
        """Log task execution details."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(self.logs_dir, f"task_{job['id']}_{timestamp}.json")

        log_data = {
            "job_id": job["id"],
            "job_name": job["name"],
            "timestamp": datetime.now().isoformat(),
            "success": success,
            "duration_seconds": duration,
            "result": str(result),
            "run_count": job["run_count"],
            "error_count": job["error_count"]
        }

        try:
            with open(log_file, 'w') as f:
                json.dump(log_data, f, indent=2)
        except Exception as e:
            logger.error(f"Error logging task execution: {e}")

    def check_pending_tasks(self):
        """Check for pending tasks in Needs_Action folder."""
        try:
            needs_action_dir = os.path.join(self.vault_path, "Needs_Action")
            if os.path.exists(needs_action_dir):
                files = os.listdir(needs_action_dir)
                if files:
                    logger.info(f"Found {len(files)} pending tasks in Needs_Action")
                    # Trigger approval workflow if needed
                    # This would integrate with the approval_workflow skill
        except Exception as e:
            logger.error(f"Error checking pending tasks: {e}")

    def run_gmail_watcher(self):
        """Run Gmail watcher task."""
        if self.config["enabled_tasks"].get("gmail_watcher", False):
            try:
                from gmail_watcher import GmailWatcher
                watcher = GmailWatcher(vault_path=self.vault_path)
                watcher.run_single_check()
            except Exception as e:
                logger.error(f"Error in Gmail watcher task: {e}")

    def run_whatsapp_watcher(self):
        """Run WhatsApp watcher task."""
        if self.config["enabled_tasks"].get("whatsapp_watcher", False):
            try:
                from whatsapp_watcher import WhatsAppWatcher
                watcher = WhatsAppWatcher(vault_path=self.vault_path)
                watcher.run_single_check()
            except Exception as e:
                logger.error(f"Error in WhatsApp watcher task: {e}")

    def run_linkedin_watcher(self):
        """Run LinkedIn watcher task."""
        if self.config["enabled_tasks"].get("linkedin_watcher", False):
            try:
                from linkedin_watcher import LinkedInWatcher
                watcher = LinkedInWatcher(vault_path=self.vault_path)
                watcher.run_single_check()
            except Exception as e:
                logger.error(f"Error in LinkedIn watcher task: {e}")

    def run_linkedin_poster(self):
        """Run LinkedIn poster task."""
        if self.config["enabled_tasks"].get("linkedin_poster", False):
            try:
                from linkedin_poster import LinkedInPoster
                poster = LinkedInPoster(vault_path=self.vault_path)
                # Create approval request for new post
                poster.auto_generate_and_post()
            except Exception as e:
                logger.error(f"Error in LinkedIn poster task: {e}")

    def run_email_sender(self):
        """Run email sender task."""
        if self.config["enabled_tasks"].get("email_sender", False):
            try:
                from email_sender import EmailSender
                sender = EmailSender(vault_path=self.vault_path)
                # Process approved emails
                sender.run()
            except Exception as e:
                logger.error(f"Error in email sender task: {e}")

    def run_approval_workflow(self):
        """Run approval workflow check."""
        if self.config["enabled_tasks"].get("approval_workflow", False):
            try:
                # Check for timeout approvals
                from approval_workflow import ApprovalWorkflow
                workflow = ApprovalWorkflow(vault_path=self.vault_path)
                workflow.check_timeout_approvals()
            except Exception as e:
                logger.error(f"Error in approval workflow task: {e}")

    def backup_vault(self):
        """Backup the vault directory."""
        try:
            import shutil
            backup_dir = f"{self.vault_path}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copytree(self.vault_path, backup_dir)
            logger.info(f"Vault backed up to: {backup_dir}")
        except Exception as e:
            logger.error(f"Error backing up vault: {e}")

    def cleanup_logs(self):
        """Clean up old log files."""
        try:
            # Remove logs older than 30 days
            cutoff_date = datetime.now() - timedelta(days=30)
            logs_cleaned = 0

            for root, dirs, files in os.walk(self.vault_path):
                for file in files:
                    if file.endswith('.log') or file.startswith('task_') and file.endswith('.json'):
                        file_path = os.path.join(root, file)
                        file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                        if file_mtime < cutoff_date:
                            os.remove(file_path)
                            logs_cleaned += 1

            logger.info(f"Cleaned up {logs_cleaned} old log files")
        except Exception as e:
            logger.error(f"Error cleaning up logs: {e}")

    def initialize_default_schedules(self):
        """Initialize default schedules from config."""
        default_schedules = self.config.get("default_schedule", {})

        # Schedule watchers
        if "gmail_check" in default_schedules:
            self.schedule_task("gmail_watcher", default_schedules["gmail_check"], self.run_gmail_watcher)

        if "whatsapp_check" in default_schedules:
            self.schedule_task("whatsapp_watcher", default_schedules["whatsapp_check"], self.run_whatsapp_watcher)

        if "linkedin_check" in default_schedules:
            self.schedule_task("linkedin_watcher", default_schedules["linkedin_check"], self.run_linkedin_watcher)

        if "linkedin_post" in default_schedules:
            self.schedule_task("linkedin_poster", default_schedules["linkedin_post"], self.run_linkedin_poster)

        # Schedule maintenance tasks
        if "backup_vault" in default_schedules:
            self.schedule_task("backup_vault", default_schedules["backup_vault"], self.backup_vault)

        if "cleanup_logs" in default_schedules:
            self.schedule_task("cleanup_logs", default_schedules["cleanup_logs"], self.cleanup_logs)

        # Schedule approval workflow check
        self.schedule_task("approval_workflow", "*/30 * * * *", self.run_approval_workflow)

        # Schedule email sender
        self.schedule_task("email_sender", "*/1 * * * *", self.run_email_sender)

    def run_scheduler(self):
        """Run the scheduler loop."""
        logger.info("Starting scheduler...")
        self.running = True

        # Initialize default schedules
        self.initialize_default_schedules()

        # Load saved schedules
        self.load_job_schedules()

        try:
            while self.running:
                # Check all jobs
                now = datetime.now()

                for job_id, job in self.jobs.items():
                    if job["enabled"] and job["next_run"] and now >= job["next_run"]:
                        # Run job in thread
                        thread = threading.Thread(target=self.run_scheduled_task, args=(job_id,))
                        thread.daemon = True
                        thread.start()

                        # Update next run time
                        cron = croniter(job["schedule"])
                        job["next_run"] = cron.get_next(datetime)

                # Sleep for a short interval
                time.sleep(30)  # Check every 30 seconds

        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
            self.running = False
        except Exception as e:
            logger.error(f"Error in scheduler: {e}")
            self.running = False

    def stop(self):
        """Stop the scheduler."""
        self.running = False

    def list_scheduled_jobs(self) -> List[Dict]:
        """List all scheduled jobs."""
        job_list = []
        for job_id, job in self.jobs.items():
            job_info = {
                "id": job_id,
                "name": job["name"],
                "schedule": job["schedule"],
                "enabled": job["enabled"],
                "next_run": job["next_run"].isoformat() if job["next_run"] else None,
                "last_run": job["last_run"],
                "run_count": job["run_count"],
                "error_count": job["error_count"]
            }
            job_list.append(job_info)
        return job_list

if __name__ == "__main__":
    # For testing
    scheduler = Scheduler()

    # List current schedules
    print("Current scheduled jobs:")
    for job in scheduler.list_scheduled_jobs():
        print(f"- {job['name']}: {job['schedule']} (Next: {job['next_run']})")

    # Run scheduler
    try:
        scheduler.run_scheduler()
    except KeyboardInterrupt:
        scheduler.stop()
        print("\nScheduler stopped.")