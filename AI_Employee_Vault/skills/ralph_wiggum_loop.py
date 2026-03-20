"""
Ralph Wiggum Loop Skill for AI Employee - Gold Tier
Implements the Ralph Wiggum pattern for autonomous multi-step task completion.
"""

import os
import json
import logging
import threading
import time
from datetime import datetime
from typing import Dict, List, Any, Callable

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ralph_wiggum_loop.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RalphWiggumLoop:
    """
    Skill to implement Ralph Wiggum loops for autonomous multi-step task completion.
    The Ralph Wiggum pattern keeps Claude iterating until multi-step tasks are complete.
    """

    def __init__(self, vault_path="./"):
        self.vault_path = vault_path
        self.loop_dir = os.path.join(vault_path, "Ralph_Loops")
        self.state_dir = os.path.join(vault_path, "Loop_States")
        self.tasks_dir = os.path.join(vault_path, "Loop_Tasks")
        self.config_dir = os.path.join(vault_path, "Config")
        self.loop_config_file = os.path.join(self.config_dir, "loop_config.json")

        # Ensure directories exist
        os.makedirs(self.loop_dir, exist_ok=True)
        os.makedirs(self.state_dir, exist_ok=True)
        os.makedirs(self.tasks_dir, exist_ok=True)
        os.makedirs(self.config_dir, exist_ok=True)

        # Load loop configuration
        self.loop_config = self._load_loop_config()

        # Active loops tracking
        self.active_loops = {}

    def _load_loop_config(self) -> Dict[str, Any]:
        """Load loop configuration."""
        if os.path.exists(self.loop_config_file):
            with open(self.loop_config_file, 'r') as f:
                return json.load(f)
        else:
            # Create default loop configuration
            default_config = {
                "default_max_iterations": 10,
                "default_timeout": 3600,  # 1 hour
                "check_interval": 5,  # seconds
                "enable_state_persistence": True,
                "enable_parallel_loops": True
            }
            with open(self.loop_config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            logger.info(f"[OK] Created default loop configuration: {self.loop_config_file}")
            return default_config

    def create_loop(self, task_description: str, max_iterations: int = None, timeout: int = None) -> str:
        """Create a Ralph Wiggum loop for a task."""
        max_iterations = max_iterations or self.loop_config["default_max_iterations"]
        timeout = timeout or self.loop_config["default_timeout"]

        # Create loop ID
        loop_id = f"loop_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.active_loops) + 1}"

        # Create loop state
        loop_state = {
            "loop_id": loop_id,
            "task_description": task_description,
            "max_iterations": max_iterations,
            "current_iteration": 0,
            "timeout_seconds": timeout,
            "start_time": datetime.now().isoformat(),
            "status": "created",
            "steps_completed": [],
            "error_count": 0,
            "last_error": None
        }

        # Save initial state
        state_file = os.path.join(self.state_dir, f"state_{loop_id}.json")
        with open(state_file, 'w') as f:
            json.dump(loop_state, f, indent=2)

        # Add to active loops if not already running
        if loop_id not in self.active_loops:
            self.active_loops[loop_id] = {
                "state": loop_state,
                "state_file": state_file,
                "thread": None,
                "stop_event": threading.Event()
            }

        logger.info(f"[OK] Ralph Wiggum loop created: {loop_id}")
        return loop_id

    def execute_loop(self, loop_id: str, task_function: Callable, *args, **kwargs) -> bool:
        """Execute a Ralph Wiggum loop with the given task function."""
        if loop_id not in self.active_loops:
            logger.error(f"[ERROR] Loop {loop_id} not found")
            return False

        loop_info = self.active_loops[loop_id]
        state = loop_info["state"]
        stop_event = loop_info["stop_event"]

        logger.info(f"Starting Ralph Wiggum loop execution: {loop_id}")

        try:
            while not stop_event.is_set():
                # Check if we've exceeded max iterations
                if state["current_iteration"] >= state["max_iterations"]:
                    logger.info(f"[OK] Loop {loop_id} completed - max iterations reached")
                    state["status"] = "completed_max_iterations"
                    break

                # Check if timeout has been exceeded
                start_time = datetime.fromisoformat(state["start_time"])
                if (datetime.now() - start_time).total_seconds() > state["timeout_seconds"]:
                    logger.info(f"[OK] Loop {loop_id} timed out")
                    state["status"] = "timeout"
                    break

                # Execute the task
                try:
                    task_result = task_function(*args, **kwargs)

                    # Update state based on result
                    state["current_iteration"] += 1
                    state["steps_completed"].append({
                        "iteration": state["current_iteration"],
                        "timestamp": datetime.now().isoformat(),
                        "result": str(task_result),
                        "completed": True
                    })

                    # Check if task is complete
                    if self._is_task_complete(task_result, state["task_description"]):
                        logger.info(f"[OK] Loop {loop_id} completed - task finished")
                        state["status"] = "completed_successfully"
                        break

                except Exception as e:
                    logger.error(f"[ERROR] Error in loop {loop_id} iteration {state['current_iteration']}: {e}")
                    state["error_count"] += 1
                    state["last_error"] = str(e)

                    # If too many errors, abort
                    if state["error_count"] > 5:
                        state["status"] = "error_limit_exceeded"
                        break

                # Update state file
                with open(loop_info["state_file"], 'w') as f:
                    json.dump(state, f, indent=2)

                # Sleep for check interval
                time.sleep(self.loop_config["check_interval"])

            # Final update to state
            state["end_time"] = datetime.now().isoformat()
            with open(loop_info["state_file"], 'w') as f:
                json.dump(state, f, indent=2)

            logger.info(f"[OK] Loop {loop_id} execution completed with status: {state['status']}")
            return True

        except Exception as e:
            logger.error(f"[ERROR] Fatal error in loop {loop_id}: {e}")
            state["status"] = "fatal_error"
            state["last_error"] = str(e)
            with open(loop_info["state_file"], 'w') as f:
                json.dump(state, f, indent=2)
            return False

    def _is_task_complete(self, result: Any, task_description: str) -> bool:
        """Determine if the task is complete based on result and description."""
        # This is a simple heuristic - in a real implementation, this would be more sophisticated
        if isinstance(result, dict):
            return result.get("completed", False)

        # If result is a string, check if it contains completion indicators
        if isinstance(result, str):
            completion_indicators = ["complete", "done", "finished", "success", "completed"]
            result_lower = result.lower()
            return any(indicator in result_lower for indicator in completion_indicators)

        # Default to not complete
        return False

    def run_autonomous_task(self, task_description: str, task_function: Callable, *args, max_iterations: int = 10, timeout: int = 3600) -> str:
        """Run an autonomous task using Ralph Wiggum loop pattern."""
        # Create the loop
        loop_id = self.create_loop(task_description, max_iterations, timeout)

        # Execute the loop in a separate thread
        def loop_thread():
            self.execute_loop(loop_id, task_function, *args)

        thread = threading.Thread(target=loop_thread)
        self.active_loops[loop_id]["thread"] = thread
        thread.start()

        logger.info(f"[OK] Autonomous task started in loop: {loop_id}")
        return loop_id

    def manage_loops(self):
        """Manage all active loops (this would typically run in a monitoring thread)."""
        logger.info("Starting Ralph Wiggum loop management...")
        return True

    def stop_loop(self, loop_id: str) -> bool:
        """Stop a specific loop."""
        if loop_id not in self.active_loops:
            logger.error(f"[ERROR] Loop {loop_id} not found")
            return False

        loop_info = self.active_loops[loop_id]

        # Set stop event
        loop_info["stop_event"].set()

        # Wait for thread to finish
        if loop_info["thread"] and loop_info["thread"].is_alive():
            loop_info["thread"].join(timeout=5)  # Wait up to 5 seconds

        # Update state
        state = loop_info["state"]
        if state["status"] not in ["completed_successfully", "completed_max_iterations", "timeout", "error_limit_exceeded", "fatal_error"]:
            state["status"] = "stopped_by_user"
            state["end_time"] = datetime.now().isoformat()

            with open(loop_info["state_file"], 'w') as f:
                json.dump(state, f, indent=2)

        logger.info(f"[OK] Loop {loop_id} stopped")
        return True

    def get_loop_status(self, loop_id: str) -> Dict[str, Any]:
        """Get status of a specific loop."""
        if loop_id not in self.active_loops:
            return {"error": f"Loop {loop_id} not found"}

        loop_info = self.active_loops[loop_id]
        state = loop_info["state"]

        return {
            "loop_id": loop_id,
            "status": state["status"],
            "current_iteration": state["current_iteration"],
            "max_iterations": state["max_iterations"],
            "steps_completed": len(state["steps_completed"]),
            "error_count": state["error_count"],
            "start_time": state["start_time"],
            "end_time": state.get("end_time"),
            "is_active": not loop_info["stop_event"].is_set()
        }

    def get_all_loops_status(self) -> Dict[str, Any]:
        """Get status of all loops."""
        status = {}
        for loop_id in self.active_loops:
            status[loop_id] = self.get_loop_status(loop_id)
        return status

    def create_complex_task_loop(self, task_plan: Dict[str, Any]) -> str:
        """Create a loop for a complex task with multiple steps."""
        def execute_complex_task():
            """Execute complex task based on plan."""
            completed_steps = []
            failed_steps = []

            for step in task_plan.get("steps", []):
                try:
                    # Execute step
                    step_result = self._execute_task_step(step)
                    completed_steps.append({
                        "step": step,
                        "result": step_result,
                        "completed_at": datetime.now().isoformat()
                    })

                    # Check if we should continue
                    if not step_result.get("continue", True):
                        break

                except Exception as e:
                    failed_steps.append({
                        "step": step,
                        "error": str(e),
                        "failed_at": datetime.now().isoformat()
                    })

            return {
                "completed_steps": completed_steps,
                "failed_steps": failed_steps,
                "completed": len(failed_steps) == 0,
                "total_steps": len(task_plan.get("steps", []))
            }

        # Create loop for complex task
        loop_id = self.run_autonomous_task(
            task_plan["task_description"],
            execute_complex_task,
            max_iterations=task_plan.get("max_iterations", 10),
            timeout=task_plan.get("timeout", 3600)
        )

        # Save task plan
        plan_file = os.path.join(self.tasks_dir, f"task_plan_{loop_id}.json")
        with open(plan_file, 'w') as f:
            json.dump(task_plan, f, indent=2)

        return loop_id

    def _execute_task_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single task step."""
        step_type = step.get("type", "generic")
        step_details = step.get("details", {})

        # This is a simulation - in a real implementation, this would execute specific actions
        # based on the step type and details
        result = {
            "step_type": step_type,
            "success": True,
            "result": f"Executed {step_type} step",
            "timestamp": datetime.now().isoformat()
        }

        logger.info(f"Executed step: {step_type}")
        return result

    def run_single_check(self):
        """Run single check for Ralph Wiggum loops."""
        logger.info("Running Ralph Wiggum loop check...")

        # Get status of all loops
        all_statuses = self.get_all_loops_status()

        # Log summary
        active_loops = [loop_id for loop_id, status in all_statuses.items() if status.get("is_active", False)]
        completed_loops = [loop_id for loop_id, status in all_statuses.items() if not status.get("is_active", False)]

        logger.info(f"[OK] Loop check completed. Active: {len(active_loops)}, Completed: {len(completed_loops)}")
        return True

if __name__ == "__main__":
    # For testing
    ralph_loop = RalphWiggumLoop()

    # Create a simple task function to test the loop
    state = {"counter": 0}
    def test_task():
        state["counter"] += 1
        counter = state["counter"]
        logger.info(f"Test task iteration {counter}")
        if counter >= 3:  # Simulate task completion
            return {"completed": True, "result": "Task completed after 3 iterations"}
        else:
            return {"completed": False, "result": f"Still working, iteration {counter}"}

    # Create and run a loop
    loop_id = ralph_loop.run_autonomous_task("Test autonomous task", test_task, max_iterations=5)
    print(f"[OK] Started test loop: {loop_id}")

    # Wait a bit for the loop to run
    time.sleep(10)

    # Check status
    status = ralph_loop.get_loop_status(loop_id)
    print(f"Loop status: {status}")

    # Run a check
    ralph_loop.run_single_check()
    print("[OK] Ralph Wiggum loop check completed successfully")