"""
Scheduler Skill for AI Employee
Implements basic scheduling via cron or Task Scheduler for automated task execution.
"""

import os
import json
import logging
import platform
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Scheduler:
    """
    Basic scheduling skill for automated task execution.
    Supports cron (Linux/Mac) and Task Scheduler (Windows).
    """

    def __init__(self, vault_path="./"):
        self.vault_path = vault_path
        self.schedules_dir = os.path.join(vault_path, "Schedules")
        self.logs_dir = os.path.join(vault_path, "Schedule_Logs")
        self.config_file = os.path.join(vault_path, "schedule_config.json")

        # Ensure directories exist
        os.makedirs(self.schedules_dir, exist_ok=True)
        os.makedirs(self.logs_dir, exist_ok=True)

        # Load configuration
        self.config = self.load_config()

        # Detect OS
        self.os_type = platform.system()

    def load_config(self) -> Dict:
        """Load schedule configuration."""
        default_config = {
            "timezone": "UTC",
            "default_user": os.getenv("USERNAME") or os.getenv("USER"),
            "enabled": True,
            "schedules": []
        }

        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            else:
                # Create default config
                with open(self.config_file, 'w') as f:
                    json.dump(default_config, f, indent=2)
                return default_config
        except Exception as e:
            logger.error(f"Error loading config: {str(e)}")
            return default_config

    def save_config(self):
        """Save schedule configuration."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving config: {str(e)}")

    def create_schedule(self, name: str, command: str, schedule: str, description: str = "") -> str:
        """Create a new schedule.

        Args:
            name: Schedule name
            command: Command to execute
            schedule: Cron format (Linux/Mac) or Windows Task Scheduler format
            description: Schedule description

        Returns:
            Schedule ID
        """
        schedule_id = datetime.now().strftime("SCHED_%Y%m%d_%H%M%S")

        schedule_entry = {
            "id": schedule_id,
            "name": name,
            "command": command,
            "schedule": schedule,
            "description": description,
            "created": datetime.now().isoformat(),
            "enabled": True,
            "last_run": None,
            "next_run": None,
            "run_count": 0,
            "success_count": 0,
            "failure_count": 0
        }

        # Add to config
        self.config["schedules"].append(schedule_entry)
        self.save_config()

        # Create actual schedule based on OS
        if self.os_type == "Windows":
            self.create_windows_task(schedule_entry)
        else:  # Linux/Mac
            self.create_cron_job(schedule_entry)

        logger.info(f"Created schedule: {name} ({schedule_id})")
        return schedule_id

    def create_cron_job(self, schedule_entry: Dict):
        """Create a cron job (Linux/Mac)."""
        try:
            # Create cron entry
            cron_line = f"{schedule_entry['schedule']} {schedule_entry['command']} >> {os.path.join(self.logs_dir, schedule_entry['id'])}.log 2>&1"

            # Add to crontab
            result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
            existing_crontab = result.stdout if result.returncode == 0 else ""

            # Add comment and new job
            new_crontab = existing_crontab + f"\n# AI Employee Schedule: {schedule_entry['name']} ({schedule_entry['id']})\n{cron_line}\n"

            # Install new crontab
            process = subprocess.Popen(['crontab', '-'], stdin=subprocess.PIPE, text=True)
            process.communicate(input=new_crontab)

            logger.info(f"Added cron job for {schedule_entry['name']}")

        except Exception as e:
            logger.error(f"Error creating cron job: {str(e)}")

    def create_windows_task(self, schedule_entry: Dict):
        """Create a Windows Task Scheduler task."""
        try:
            # Parse cron-like schedule for Windows
            # Convert to Windows Task Scheduler format
            schedule_parts = schedule_entry['schedule'].split()

            # Create PowerShell script to create task
            ps_script = f"""
$Action = New-ScheduledTaskAction -Execute "python.exe" -Argument "{schedule_entry['command'].replace('"', '""')}"
$Trigger = New-ScheduledTaskTrigger -Daily -At "09:00"  # Simplified - would parse cron format
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
$Task = New-ScheduledTask -Action $Action -Trigger $Trigger -Settings $Settings
Register-ScheduledTask -TaskName "AI_Employee_{schedule_entry['id']}" -InputObject $Task
"""

            # Save PowerShell script
            ps_file = os.path.join(self.schedules_dir, f"{schedule_entry['id']}_create.ps1")
            with open(ps_file, 'w') as f:
                f.write(ps_script)

            logger.info(f"Created Windows task script: {ps_file}")
            logger.info("Run the PowerShell script as Administrator to create the task")

        except Exception as e:
            logger.error(f"Error creating Windows task: {str(e)}")

    def list_schedules(self) -> List[Dict]:
        """List all schedules."""
        return self.config.get("schedules", [])

    def get_schedule(self, schedule_id: str) -> Optional[Dict]:
        """Get a specific schedule by ID."""
        for schedule in self.config.get("schedules", []):
            if schedule["id"] == schedule_id:
                return schedule
        return None

    def enable_schedule(self, schedule_id: str) -> bool:
        """Enable a schedule."""
        schedule = self.get_schedule(schedule_id)
        if schedule:
            schedule["enabled"] = True
            self.save_config()
            logger.info(f"Enabled schedule: {schedule_id}")
            return True
        return False

    def disable_schedule(self, schedule_id: str) -> bool:
        """Disable a schedule."""
        schedule = self.get_schedule(schedule_id)
        if schedule:
            schedule["enabled"] = False
            self.save_config()
            logger.info(f"Disabled schedule: {schedule_id}")
            return True
        return False

    def delete_schedule(self, schedule_id: str) -> bool:
        """Delete a schedule."""
        schedules = self.config.get("schedules", [])

        # Find and remove schedule
        for i, schedule in enumerate(schedules):
            if schedule["id"] == schedule_id:
                # Remove from OS scheduler
                if self.os_type == "Windows":
                    self.delete_windows_task(schedule_id)
                else:
                    self.delete_cron_job(schedule_id)

                # Remove from config
                del schedules[i]
                self.save_config()
                logger.info(f"Deleted schedule: {schedule_id}")
                return True

        return False

    def delete_cron_job(self, schedule_id: str):
        """Delete a cron job."""
        try:
            # Get current crontab
            result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
            if result.returncode != 0:
                return

            lines = result.stdout.split('\n')
            new_lines = []
            skip_next = False

            for line in lines:
                if skip_next:
                    skip_next = False
                    continue
                if schedule_id in line:
                    # Skip this line and the comment before it
                    if new_lines and new_lines[-1].startswith("# AI Employee Schedule:"):
                        new_lines.pop()
                    continue
                new_lines.append(line)

            # Update crontab
            new_crontab = '\n'.join(new_lines)
            process = subprocess.Popen(['crontab', '-'], stdin=subprocess.PIPE, text=True)
            process.communicate(input=new_crontab)

            logger.info(f"Removed cron job: {schedule_id}")

        except Exception as e:
            logger.error(f"Error deleting cron job: {str(e)}")

    def delete_windows_task(self, schedule_id: str):
        """Delete a Windows task."""
        try:
            # Create PowerShell script to delete task
            ps_script = f"Unregister-ScheduledTask -TaskName 'AI_Employee_{schedule_id}' -Confirm:$false"

            ps_file = os.path.join(self.schedules_dir, f"{schedule_id}_delete.ps1")
            with open(ps_file, 'w') as f:
                f.write(ps_script)

            logger.info(f"Created Windows task deletion script: {ps_file}")
            logger.info("Run the PowerShell script as Administrator to delete the task")

        except Exception as e:
            logger.error(f"Error deleting Windows task: {str(e)}")

    def create_common_schedules(self):
        """Create common schedules for AI Employee tasks."""
        common_schedules = [
            {
                "name": "Daily Business Review",
                "command": "python orchestrator.py --single",
                "schedule": "0 9 * * *",  # 9 AM daily
                "description": "Run daily business review and create summary"
            },
            {
                "name": "LinkedIn Post Scheduler",
                "command": "python skills/linkedin_poster.py --auto",
                "schedule": "0 10 * * 1,3,5",  # 10 AM on Mon, Wed, Fri
                "description": "Auto-generate and schedule LinkedIn posts"
            },
            {
                "name": "Email Digest Sender",
                "command": "python skills/email_sender.py --digest",
                "schedule": "0 17 * * 1-5",  # 5 PM weekdays
                "description": "Send daily email digest to team"
            },
            {
                "name": "Weekly Report Generator",
                "command": "python orchestrator.py --weekly-report",
                "schedule": "0 8 * * 1",  # 8 AM on Mondays
                "description": "Generate and send weekly performance report"
            },
            {
                "name": "Approval Expiry Check",
                "command": "python skills/approval_workflow.py --check-expired",
                "schedule": "*/30 * * * *",  # Every 30 minutes
                "description": "Check for expired approval requests"
            }
        ]

        created_ids = []
        for schedule in common_schedules:
            schedule_id = self.create_schedule(
                schedule["name"],
                schedule["command"],
                schedule["schedule"],
                schedule["description"]
            )
            created_ids.append(schedule_id)

        logger.info(f"Created {len(created_ids)} common schedules")
        return created_ids

    def create_windows_task_scheduler_xml(self, schedule_entry: Dict) -> str:
        """Create Windows Task Scheduler XML configuration."""
        xml_content = f"""<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Date>{datetime.now().isoformat()}</Date>
    <Author>AI Employee</Author>
    <Description>{schedule_entry['description']}</Description>
  </RegistrationInfo>
  <Triggers>
    <CalendarTrigger>
      <StartBoundary>{datetime.now().isoformat()}</StartBoundary>
      <Enabled>true</Enabled>
      <ScheduleByDay>
        <DaysInterval>1</DaysInterval>
      </ScheduleByDay>
    </CalendarTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <LogonType>InteractiveToken</LogonType>
      <UserId>{self.config.get('default_user', '')}</UserId>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT1H</ExecutionTimeLimit>
    <Priority>6</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>python.exe</Command>
      <Arguments>{schedule_entry['command']}</Arguments>
      <WorkingDirectory>{self.vault_path}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>"""

        return xml_content

    def monitor_schedules(self):
        """Monitor schedule execution and update logs."""
        logger.info("Starting schedule monitoring...")

        while True:
            try:
                # Check for new log files
                for schedule in self.config.get("schedules", []):
                    log_file = os.path.join(self.logs_dir, f"{schedule['id']}.log")

                    if os.path.exists(log_file):
                        # Check if log was updated recently
                        file_mtime = datetime.fromtimestamp(os.path.getmtime(log_file))
                        if datetime.now() - file_mtime < timedelta(minutes=5):
                            # Schedule just ran
                            schedule["last_run"] = file_mtime.isoformat()
                            schedule["run_count"] += 1

                            # Check if successful (simplified check)
                            with open(log_file, 'r') as f:
                                log_content = f.read()
                                if "ERROR" not in log_content.upper():
                                    schedule["success_count"] += 1
                                else:
                                    schedule["failure_count"] += 1

                self.save_config()
                time.sleep(60)  # Check every minute

            except KeyboardInterrupt:
                logger.info("Schedule monitoring stopped")
                break
            except Exception as e:
                logger.error(f"Error monitoring schedules: {str(e)}")
                time.sleep(300)  # Wait 5 minutes before retry

    def create_schedule_summary(self) -> str:
        """Create a summary of all schedules."""
        schedules = self.list_schedules()

        summary = f"""# Schedule Summary

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**OS:** {self.os_type}
**Schedules:** {len(schedules)}

## Active Schedules
"""

        for schedule in schedules:
            status = "✅ Enabled" if schedule.get("enabled", True) else "❌ Disabled"
            summary += f"""
### {schedule['name']} {status}
- **ID:** {schedule['id']}
- **Schedule:** {schedule['schedule']}
- **Command:** {schedule['command']}
- **Description:** {schedule['description']}
- **Created:** {schedule['created']}
- **Last Run:** {schedule.get('last_run', 'Never')}
- **Run Count:** {schedule.get('run_count', 0)}
- **Success Rate:** {schedule.get('success_count', 0)}/{schedule.get('run_count', 0)}
"""

        summary += f"""
## Management Commands
- **List schedules:** python skills/scheduler.py --list
- **Create schedule:** python skills/scheduler.py --create "Name" "Command" "Schedule"
- **Enable/Disable:** python skills/scheduler.py --enable/--disable "Schedule_ID"
- **Delete schedule:** python skills/scheduler.py --delete "Schedule_ID"

## Schedule Format
- **Linux/Mac (Cron):** "0 9 * * *" (9 AM daily)\n- **Windows:** Use Task Scheduler GUI or PowerShell scripts
"""

        return summary

if __name__ == "__main__":
    # For testing
    scheduler = Scheduler()

    # Create common schedules
    schedule_ids = scheduler.create_common_schedules()
    print(f"Created {len(schedule_ids)} common schedules")

    # Show summary
    print("\n" + scheduler.create_schedule_summary())