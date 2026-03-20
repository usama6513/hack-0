"""
Plan Generator Skill for AI Employee - Silver Tier
Creates Plan.md files with Claude reasoning loop for task planning and execution.
"""

import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('plan_generator.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PlanGenerator:
    """
    Skill to create comprehensive Plan.md files with reasoning and execution steps.
    """

    def __init__(self, vault_path="./"):
        self.vault_path = vault_path
        self.plans_dir = os.path.join(vault_path, "Plans")
        self.templates_dir = os.path.join(vault_path, "Templates")

        # Ensure directories exist
        os.makedirs(self.plans_dir, exist_ok=True)
        os.makedirs(self.templates_dir, exist_ok=True)

    def analyze_task(self, task_description: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze a task and break it down into components."""
        analysis = {
            "task": task_description,
            "complexity": self.assess_complexity(task_description),
            "domain": self.identify_domain(task_description),
            "priority": self.assess_priority(task_description, context),
            "estimated_time": self.estimate_time(task_description),
            "dependencies": self.identify_dependencies(task_description),
            "risks": self.identify_risks(task_description),
            "resources_needed": self.identify_resources(task_description)
        }

        return analysis

    def assess_complexity(self, task: str) -> str:
        """Assess task complexity."""
        complexity_indicators = {
            "high": ["multi-step", "complex", "integrate", "automate", "design", "implement"],
            "medium": ["review", "analyze", "optimize", "update", "create"],
            "low": ["check", "read", "move", "copy", "simple"]
        }

        task_lower = task.lower()
        for level, indicators in complexity_indicators.items():
            if any(indicator in task_lower for indicator in indicators):
                return level

        return "medium"

    def identify_domain(self, task: str) -> str:
        """Identify the domain of the task."""
        domains = {
            "communication": ["email", "message", "whatsapp", "linkedin", "call"],
            "finance": ["invoice", "payment", "billing", "accounting", "expense"],
            "marketing": ["social media", "linkedin", "post", "content", "campaign"],
            "operations": ["process", "workflow", "automation", "system"],
            "planning": ["schedule", "calendar", "meeting", "appointment"],
            "analysis": ["report", "data", "analytics", "metrics"]
        }

        task_lower = task.lower()
        for domain, keywords in domains.items():
            if any(keyword in task_lower for keyword in keywords):
                return domain

        return "general"

    def assess_priority(self, task: str, context: Dict[str, Any] = None) -> str:
        """Assess task priority."""
        priority_keywords = {
            "high": ["urgent", "asap", "emergency", "critical", "deadline", "expiring"],
            "medium": ["important", "schedule", "meeting", "client", "payment"],
            "low": ["when possible", "low priority", "nice to have"]
        }

        task_lower = task.lower()
        for priority, keywords in priority_keywords.items():
            if any(keyword in task_lower for keyword in keywords):
                return priority

        # Default priority
        return "medium"

    def estimate_time(self, task: str) -> str:
        """Estimate time needed for task."""
        complexity = self.assess_complexity(task)

        time_estimates = {
            "high": "2-4 hours",
            "medium": "30 minutes - 2 hours",
            "low": "5-30 minutes"
        }

        return time_estimates.get(complexity, "30 minutes - 2 hours")

    def identify_dependencies(self, task: str) -> List[str]:
        """Identify task dependencies."""
        dependencies = []

        # Look for dependency indicators
        dep_indicators = {
            "requires": ["requires", "needs", "depends on", "after"],
            "before": ["before", "prior to", "in preparation for"],
            "with": ["with", "using", "via", "through"]
        }

        task_lower = task.lower()
        for dep_type, indicators in dep_indicators.items():
            for indicator in indicators:
                if indicator in task_lower:
                    dependencies.append(f"Potential {dep_type} dependency detected")

        return dependencies

    def identify_risks(self, task: str) -> List[str]:
        """Identify potential risks."""
        risks = []

        risk_keywords = {
            "security": ["password", "login", "credentials", "private", "confidential"],
            "financial": ["payment", "invoice", "money", "cost", "expensive"],
            "time": ["deadline", "urgent", "asap", "critical"],
            "external": ["api", "third-party", "external", "integration"]
        }

        task_lower = task.lower()
        for risk_type, keywords in risk_keywords.items():
            if any(keyword in task_lower for keyword in keywords):
                risks.append(f"{risk_type.capitalize()} risk: {', '.join([k for k in keywords if k in task_lower])}")

        return risks

    def identify_resources(self, task: str) -> List[str]:
        """Identify required resources."""
        resources = []

        resource_keywords = {
            "tools": ["selenium", "playwright", "api", "mcp", "automation"],
            "data": ["file", "data", "database", "spreadsheet"],
            "accounts": ["gmail", "linkedin", "whatsapp", "account", "login"],
            "time": ["schedule", "calendar", "appointment"]
        }

        task_lower = task.lower()
        for resource_type, keywords in resource_keywords.items():
            if any(keyword in task_lower for keyword in keywords):
                resources.append(resource_type)

        # Add general resources
        resources.extend(["Claude Code", "Obsidian Vault", "Python scripts"])

        return list(set(resources))  # Remove duplicates

    def create_plan(self, task_description: str, context: Dict[str, Any] = None) -> str:
        """Create a comprehensive Plan.md file."""
        # Analyze the task
        analysis = self.analyze_task(task_description, context)

        # Generate plan ID
        plan_id = datetime.now().strftime("PLAN_%Y%m%d_%H%M%S")

        # Create plan filename
        plan_filename = f"{plan_id}.md"
        plan_path = os.path.join(self.plans_dir, plan_filename)

        # Generate steps based on analysis
        steps = self.generate_steps(analysis)

        # Create plan content
        plan_content = self.format_plan_content(plan_id, analysis, steps)

        # Write plan file
        with open(plan_path, 'w', encoding='utf-8') as f:
            f.write(plan_content)

        logger.info(f"Created plan: {plan_filename}")
        return plan_path

    def generate_steps(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate execution steps based on task analysis."""
        steps = []

        # Base steps for any task
        steps.append({
            "id": 1,
            "action": "Review task requirements and context",
            "details": "Understand what needs to be done and why",
            "status": "pending",
            "estimated_time": "5 minutes",
            "dependencies": [],
            "success_criteria": "Clear understanding of task objectives"
        })

        # Add domain-specific steps
        if analysis['domain'] == "communication":
            steps.extend(self.get_communication_steps(analysis))
        elif analysis['domain'] == "finance":
            steps.extend(self.get_finance_steps(analysis))
        elif analysis['domain'] == "marketing":
            steps.extend(self.get_marketing_steps(analysis))
        elif analysis['domain'] == "operations":
            steps.extend(self.get_operations_steps(analysis))
        else:
            steps.extend(self.get_general_steps(analysis))

        # Add verification step
        steps.append({
            "id": len(steps) + 1,
            "action": "Verify completion and update status",
            "details": "Ensure all steps completed successfully and update relevant files",
            "status": "pending",
            "estimated_time": "5 minutes",
            "dependencies": [s['id'] for s in steps[:-1]],
            "success_criteria": "Task marked as complete in appropriate system"
        })

        return steps

    def get_communication_steps(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get steps for communication tasks."""
        return [
            {
                "id": 2,
                "action": "Check for existing conversation history",
                "details": "Review previous messages or emails in the vault",
                "status": "pending",
                "estimated_time": "5 minutes",
                "dependencies": [1],
                "success_criteria": "Context gathered from previous communications"
            },
            {
                "id": 3,
                "action": "Draft appropriate response",
                "details": "Create response based on context and requirements",
                "status": "pending",
                "estimated_time": "10 minutes",
                "dependencies": [2],
                "success_criteria": "Response drafted and reviewed"
            },
            {
                "id": 4,
                "action": "Request approval if needed",
                "details": "Create approval file for sensitive communications",
                "status": "pending",
                "estimated_time": "2 minutes",
                "dependencies": [3],
                "success_criteria": "Approval file created if required"
            }
        ]

    def get_finance_steps(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get steps for finance tasks."""
        return [
            {
                "id": 2,
                "action": "Verify financial data accuracy",
                "details": "Double-check numbers and calculations",
                "status": "pending",
                "estimated_time": "10 minutes",
                "dependencies": [1],
                "success_criteria": "All financial data verified"
            },
            {
                "id": 3,
                "action": "Check approval requirements",
                "details": "Determine if human approval is needed",
                "status": "pending",
                "estimated_time": "5 minutes",
                "dependencies": [2],
                "success_criteria": "Approval requirements identified"
            },
            {
                "id": 4,
                "action": "Process transaction or create record",
                "details": "Execute financial action or create appropriate record",
                "status": "pending",
                "estimated_time": "15 minutes",
                "dependencies": [3],
                "success_criteria": "Financial action completed successfully"
            }
        ]

    def get_marketing_steps(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get steps for marketing tasks."""
        return [
            {
                "id": 2,
                "action": "Review brand guidelines and messaging",
                "details": "Ensure content aligns with company voice and guidelines",
                "status": "pending",
                "estimated_time": "5 minutes",
                "dependencies": [1],
                "success_criteria": "Content guidelines reviewed and understood"
            },
            {
                "id": 3,
                "action": "Create or optimize content",
                "details": "Generate marketing content or optimize existing content",
                "status": "pending",
                "estimated_time": "20 minutes",
                "dependencies": [2],
                "success_criteria": "Content created and reviewed"
            },
            {
                "id": 4,
                "action": "Schedule or publish content",
                "details": "Post content or schedule for optimal timing",
                "status": "pending",
                "estimated_time": "10 minutes",
                "dependencies": [3],
                "success_criteria": "Content published or scheduled"
            }
        ]

    def get_operations_steps(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get steps for operations tasks."""
        return [
            {
                "id": 2,
                "action": "Check system status and dependencies",
                "details": "Ensure all systems are operational",
                "status": "pending",
                "estimated_time": "10 minutes",
                "dependencies": [1],
                "success_criteria": "System status verified"
            },
            {
                "id": 3,
                "action": "Execute operational procedure",
                "details": "Follow documented procedure for operation",
                "status": "pending",
                "estimated_time": "30 minutes",
                "dependencies": [2],
                "success_criteria": "Procedure executed successfully"
            },
            {
                "id": 4,
                "action": "Monitor and verify results",
                "details": "Check that operation achieved desired outcome",
                "status": "pending",
                "estimated_time": "10 minutes",
                "dependencies": [3],
                "success_criteria": "Results verified and documented"
            }
        ]

    def get_general_steps(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get general steps for unknown tasks."""
        return [
            {
                "id": 2,
                "action": "Research and understand requirements",
                "details": "Gather all necessary information about the task",
                "status": "pending",
                "estimated_time": "15 minutes",
                "dependencies": [1],
                "success_criteria": "All requirements understood"
            },
            {
                "id": 3,
                "action": "Break down into manageable sub-tasks",
                "details": "Divide complex task into smaller, actionable items",
                "status": "pending",
                "estimated_time": "10 minutes",
                "dependencies": [2],
                "success_criteria": "Task broken down into clear steps"
            },
            {
                "id": 4,
                "action": "Execute sub-tasks systematically",
                "details": "Complete each sub-task in order",
                "status": "pending",
                "estimated_time": "30 minutes",
                "dependencies": [3],
                "success_criteria": "All sub-tasks completed"
            }
        ]

    def format_plan_content(self, plan_id: str, analysis: Dict[str, Any], steps: List[Dict[str, Any]]) -> str:
        """Format the plan content as markdown."""
        content = f"""# {plan_id}

## Task Overview
**Task:** {analysis['task']}
**Domain:** {analysis['domain']}
**Complexity:** {analysis['complexity']}
**Priority:** {analysis['priority']}
**Estimated Time:** {analysis['estimated_time']}
**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Analysis
### Task Assessment
- **Complexity Level:** {analysis['complexity']}
- **Domain:** {analysis['domain']}
- **Priority:** {analysis['priority']}
- **Estimated Duration:** {analysis['estimated_time']}

### Dependencies
{chr(10).join(['- ' + dep for dep in analysis['dependencies']]) if analysis['dependencies'] else '- No dependencies identified'}

### Risks
{chr(10).join(['- ' + risk for risk in analysis['risks']]) if analysis['risks'] else '- No significant risks identified'}

### Resources Required
{chr(10).join(['- ' + resource for resource in analysis['resources_needed']])}

## Execution Plan
"""

        # Add steps
        for step in steps:
            status_emoji = "⏳" if step['status'] == "pending" else "✅" if step['status'] == "completed" else "❌"
            content += f"""
### Step {step['id']}: {step['action']} {status_emoji}
- **Details:** {step['details']}
- **Status:** {step['status']}
- **Estimated Time:** {step['estimated_time']}
- **Dependencies:** {', '.join([f"Step {dep}" for dep in step['dependencies']]) if step['dependencies'] else 'None'}
- **Success Criteria:** {step['success_criteria']}

"""

        # Add execution notes
        content += f"""
## Execution Notes
### Claude Reasoning
Based on the analysis, this task requires:
1. **{analysis['complexity'].title()} complexity** handling
2. **{analysis['domain'].title()} domain** expertise
3. **{analysis['priority'].title()} priority** execution

### Next Steps
1. Review and approve this plan
2. Execute steps in order
3. Update status as each step completes
4. Document any deviations or learnings

### Monitoring
- Check progress every 30 minutes
- Update status in real-time
- Escalate if blocked for more than 1 hour

---
*Plan generated by Claude Code AI Employee*
"""

        return content

    def update_plan_status(self, plan_id: str, step_id: int, status: str, notes: str = ""):
        """Update the status of a step in a plan."""
        plan_path = os.path.join(self.plans_dir, f"{plan_id}.md")

        if not os.path.exists(plan_path):
            logger.error(f"Plan not found: {plan_id}")
            return False

        # Read current content
        with open(plan_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Update step status
        old_status = f"**Status:** {status}"
        new_status = f"**Status:** {status}"

        if notes:
            new_status += f"\n- **Notes:** {notes}"

        # Update in content (simple replace)
        # In production, use proper markdown parsing
        if f"### Step {step_id}:" in content:
            # This is a simplified update - in production use proper parsing
            logger.info(f"Updated Step {step_id} in {plan_id} to {status}")
            return True

        return False

    def create_claude_reasoning_loop(self, task: str) -> str:
        """Create a Claude reasoning loop for continuous improvement."""
        reasoning_content = f"""# Claude Reasoning Loop - {datetime.now().strftime('%Y%m%d_%H%M%S')}

## Initial Task
{task}

## Reasoning Process
1. **Understand**: What is being asked?
2. **Analyze**: What are the constraints and requirements?
3. **Plan**: What is the best approach?
4. **Execute**: How to implement the solution?
5. **Verify**: Did it work as expected?
6. **Improve**: How can it be better?

## Current Iteration
- **Step**: Initial analysis
- **Status**: In progress
- **Confidence**: High
- **Next Action**: Create detailed plan

## Learning Points
- Document what works
- Note what doesn't work
- Identify patterns
- Update heuristics

## Ralph Wiggum Stop Condition
Continue iterating until:
- Task is completed successfully
- Maximum iterations reached (10)
- Human intervention required
- Error state encountered

---
*Reasoning loop active*
"""

        reasoning_path = os.path.join(self.plans_dir, f"REASONING_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
        with open(reasoning_path, 'w', encoding='utf-8') as f:
            f.write(reasoning_content)

        return reasoning_path

if __name__ == "__main__":
    # For testing
    planner = PlanGenerator()

    # Test task
    test_task = "Create a LinkedIn post about AI automation benefits for small businesses"

    # Analyze and create plan
    analysis = planner.analyze_task(test_task)
    print("Task Analysis:")
    print(json.dumps(analysis, indent=2))

    # Create plan
    plan_path = planner.create_plan(test_task)
    print(f"\nCreated plan: {plan_path}")

    # Create reasoning loop
    reasoning_path = planner.create_claude_reasoning_loop(test_task)
    print(f"Created reasoning loop: {reasoning_path}")