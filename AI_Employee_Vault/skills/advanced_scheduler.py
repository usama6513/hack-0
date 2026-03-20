"""
Advanced Scheduler Skill for AI Employee - Gold Tier
Handles automated posting, commenting, and other scheduled tasks for social media and Odoo.
"""

import os
import json
import logging
import schedule
import threading
import time
from datetime import datetime
from typing import Dict, List, Any, Callable

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('advanced_scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AdvancedScheduler:
    """
    Skill to handle automated posting, commenting, and scheduled tasks for social media and Odoo.
    """

    def __init__(self, vault_path="./"):
        self.vault_path = vault_path
        self.scheduler_dir = os.path.join(vault_path, "Scheduler_Tasks")
        self.config_file = os.path.join(vault_path, "scheduler_config.json")

        # Ensure directories exist
        os.makedirs(self.scheduler_dir, exist_ok=True)

        # Load configuration
        self.config = self.load_config()

        # Store task functions for all skills
        self.skill_functions = {}

        # Schedule lock to prevent concurrent execution
        self.schedule_lock = threading.Lock()

    def load_config(self) -> Dict[str, Any]:
        """Load scheduler configuration from file."""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        else:
            # Create default configuration
            default_config = {
                "tasks": {
                    "facebook_auto_post": {
                        "enabled": True,
                        "schedule": "0 9 * * 1-5",
                        "action": "facebook_api_integration.generate_and_post",
                        "params": {
                            "topic": "business automation"
                        }
                    },
                    "instagram_auto_post": {
                        "enabled": True,
                        "schedule": "0 12 * * 1-5",
                        "action": "instagram_api_integration.generate_and_post",
                        "params": {
                            "topic": "innovation"
                        }
                    },
                    "twitter_auto_post": {
                        "enabled": True,
                        "schedule": "0 15 * * 1-5",
                        "action": "twitter_api_integration.generate_and_post",
                        "params": {
                            "topic": "AI automation"
                        }
                    },
                    "odoo_daily_sync": {
                        "enabled": True,
                        "schedule": "0 6 * * *",
                        "action": "odoo_integration.sync_data",
                        "params": {
                            "data_type": "daily_operations",
                            "direction": "from_external"
                        }
                    },
                    "odoo_weekly_report": {
                        "enabled": True,
                        "schedule": "0 6 * * 1",
                        "action": "odoo_integration.get_sales_data",
                        "params": {
                            "days": 7
                        }
                    },
                    "social_media_monitoring": {
                        "enabled": True,
                        "schedule": "*/30 * * * *",
                        "action": "facebook_api_integration.get_page_posts",
                        "params": {
                            "limit": 10
                        }
                    }
                },
                "global_settings": {
                    "timezone": "UTC",
                    "max_concurrent_tasks": 3,
                    "task_timeout": 300,
                    "retry_failed_tasks": True,
                    "max_retries": 3,
                    "logging_enabled": True
                }
            }
            with open(self.config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            logger.info(f"[OK] Created default scheduler configuration: {self.config_file}")
            return default_config

    def register_skill_functions(self, skills: Dict[str, Any]):
        """Register skill functions for use in scheduled tasks."""
        self.skill_functions = skills

    def parse_cron_schedule(self, cron_expr: str) -> schedule.Job:
        """Parse a cron expression and return a schedule job."""
        parts = cron_expr.split()
        if len(parts) != 5:
            raise ValueError(f"Invalid cron expression: {cron_expr}")

        minute, hour, day, month, weekday = parts

        # Create a schedule job based on cron expression
        job = schedule.every()

        # Handle minute
        if minute == '*':
            pass  # Every minute
        elif ',' in minute:
            # Multiple values like "10,30"
            minutes = [int(m) for m in minute.split(',')]
            job.at(f"{minutes[0]:02d}:{minutes[0]:02d}")
        elif '/' in minute:
            # Every X minutes like "*/10"
            interval = int(minute.split('/')[1])
            job.minutes(interval)
        else:
            # Specific minute
            job.minute.at(minute)

        # Handle hour
        if hour != '*':
            if '/' in hour:
                # Every X hours
                interval = int(hour.split('/')[1])
                job.hours(interval)
            else:
                # Specific hour
                job.at(f"{int(hour):02d}:00")

        # Handle day
        if day != '*':
            # Specific day of month
            job.day.at(f"{int(day):02d}")

        # Handle weekday
        if weekday != '*':
            if weekday == '1-5':  # Weekdays
                job.monday.to.friday
            elif weekday == '0':  # Sunday
                job.sunday
            elif weekday == '6':  # Saturday
                job.saturday

        return job

    def execute_scheduled_task(self, task_name: str, action: str, params: Dict[str, Any] = None):
        """Execute a scheduled task with error handling and retry logic."""
        logger.info(f"Executing scheduled task: {task_name}")

        # Extract skill name and method from action
        if '.' in action:
            skill_name, method_name = action.rsplit('.', 1)
        else:
            logger.error(f"[ERROR] Invalid action format: {action}")
            return False

        # Check if skill is available
        if skill_name not in self.skill_functions:
            logger.error(f"[ERROR] Skill {skill_name} not available for task {task_name}")
            return False

        skill = self.skill_functions[skill_name]

        # Check if method exists
        if not hasattr(skill, method_name):
            logger.error(f"[ERROR] Method {method_name} not found in skill {skill_name}")
            return False

        method = getattr(skill, method_name)

        # Get retry settings
        max_retries = self.config["global_settings"].get("max_retries", 3)
        retry_failed_tasks = self.config["global_settings"].get("retry_failed_tasks", True)

        # Execute with retries
        for attempt in range(max_retries):
            try:
                with self.schedule_lock:
                    logger.info(f"Running task '{task_name}' (attempt {attempt + 1})")

                    # Execute the method with parameters
                    if params:
                        result = method(**params)
                    else:
                        result = method()

                    if result:
                        logger.info(f"[OK] Task '{task_name}' completed successfully")

                        # Log successful task execution
                        self.log_task_execution(task_name, "success", str(result))
                        return True
                    else:
                        logger.error(f"[ERROR] Task '{task_name}' failed on attempt {attempt + 1}")

                        # Log failed task execution
                        self.log_task_execution(task_name, "failed", "Task execution returned False")

                        if not retry_failed_tasks or attempt == max_retries - 1:
                            break
                        else:
                            # Wait before retry
                            time.sleep(5 * (attempt + 1))  # Exponential backoff
            except Exception as e:
                logger.error(f"[ERROR] Task '{task_name}' failed on attempt {attempt + 1} with error: {e}")

                # Log failed task execution
                self.log_task_execution(task_name, "failed", str(e))

                if not retry_failed_tasks or attempt == max_retries - 1:
                    break
                else:
                    # Wait before retry
                    time.sleep(5 * (attempt + 1))  # Exponential backoff

        logger.error(f"[ERROR] Task '{task_name}' failed after {max_retries} attempts")
        return False

    def log_task_execution(self, task_name: str, status: str, details: str):
        """Log task execution to file."""
        log_entry = {
            "task_name": task_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }

        log_file = os.path.join(self.scheduler_dir, f"task_log_{datetime.now().strftime('%Y%m%d')}.json")

        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

    def schedule_tasks(self):
        """Schedule all configured tasks."""
        logger.info("Scheduling tasks...")

        tasks = self.config.get("tasks", {})

        for task_name, task_config in tasks.items():
            if not task_config.get("enabled", False):
                logger.info(f"Task {task_name} is disabled, skipping")
                continue

            schedule_expr = task_config.get("schedule", "")
            action = task_config.get("action", "")
            params = task_config.get("params", {})

            if not schedule_expr or not action:
                logger.warning(f"Task {task_name} missing schedule or action, skipping")
                continue

            # Parse the schedule expression and create job
            try:
                # Create a wrapper function to execute the task
                def create_task_runner(name, action, params):
                    return lambda: self.execute_scheduled_task(name, action, params)

                task_runner = create_task_runner(task_name, action, params)

                # Handle simple schedule expressions (not full cron)
                if schedule_expr == "*/30 * * * *":  # Every 30 minutes
                    schedule.every(30).minutes.do(task_runner)
                elif schedule_expr == "0 9 * * 1-5":  # Weekdays at 9 AM
                    schedule.every().monday.at("09:00").do(task_runner)
                    schedule.every().tuesday.at("09:00").do(task_runner)
                    schedule.every().wednesday.at("09:00").do(task_runner)
                    schedule.every().thursday.at("09:00").do(task_runner)
                    schedule.every().friday.at("09:00").do(task_runner)
                elif schedule_expr == "0 12 * * 1-5":  # Weekdays at 12 PM
                    schedule.every().monday.at("12:00").do(task_runner)
                    schedule.every().tuesday.at("12:00").do(task_runner)
                    schedule.every().wednesday.at("12:00").do(task_runner)
                    schedule.every().thursday.at("12:00").do(task_runner)
                    schedule.every().friday.at("12:00").do(task_runner)
                elif schedule_expr == "0 15 * * 1-5":  # Weekdays at 3 PM
                    schedule.every().monday.at("15:00").do(task_runner)
                    schedule.every().tuesday.at("15:00").do(task_runner)
                    schedule.every().wednesday.at("15:00").do(task_runner)
                    schedule.every().thursday.at("15:00").do(task_runner)
                    schedule.every().friday.at("15:00").do(task_runner)
                elif schedule_expr == "0 6 * * *":  # Daily at 6 AM
                    schedule.every().day.at("06:00").do(task_runner)
                elif schedule_expr == "0 6 * * 1":  # Weekly on Monday at 6 AM
                    schedule.every().monday.at("06:00").do(task_runner)
                elif schedule_expr == "0 10,16 * * 1-5":  # Weekdays at 10 AM and 4 PM
                    schedule.every().monday.at("10:00").do(task_runner)
                    schedule.every().tuesday.at("10:00").do(task_runner)
                    schedule.every().wednesday.at("10:00").do(task_runner)
                    schedule.every().thursday.at("10:00").do(task_runner)
                    schedule.every().friday.at("10:00").do(task_runner)
                    schedule.every().monday.at("16:00").do(task_runner)
                    schedule.every().tuesday.at("16:00").do(task_runner)
                    schedule.every().wednesday.at("16:00").do(task_runner)
                    schedule.every().thursday.at("16:00").do(task_runner)
                    schedule.every().friday.at("16:00").do(task_runner)
                else:
                    # Handle other cron expressions
                    logger.warning(f"Unsupported schedule expression for {task_name}: {schedule_expr}, using default")

                logger.info(f"[OK] Scheduled task '{task_name}' with expression '{schedule_expr}'")

            except Exception as e:
                logger.error(f"[ERROR] Failed to schedule task {task_name}: {e}")

    def run_scheduler(self):
        """Run the task scheduler continuously."""
        logger.info("Starting advanced scheduler...")

        # Schedule all tasks
        self.schedule_tasks()

        # Run the scheduler
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

    def run_single_check(self):
        """Run single check for scheduler."""
        logger.info("Running scheduler check...")

        # Just verify the configuration is loaded
        task_count = len(self.config.get("tasks", {}))
        logger.info(f"[OK] Scheduler configured with {task_count} tasks")
        return True

if __name__ == "__main__":
    # For testing
    scheduler = AdvancedScheduler()
    print(f"Scheduler loaded with {len(scheduler.config.get('tasks', {}))} tasks")