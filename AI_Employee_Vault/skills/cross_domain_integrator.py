"""
Cross Domain Integrator Skill for AI Employee - Gold Tier
Integrates personal and business domains for unified workflow.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cross_domain_integrator.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CrossDomainIntegrator:
    """
    Skill to integrate personal and business domains for unified operations.
    """

    def __init__(self, vault_path="./"):
        self.vault_path = vault_path
        self.cross_domain_dir = os.path.join(vault_path, "Cross_Domain")
        self.personal_dir = os.path.join(vault_path, "Personal")
        self.business_dir = os.path.join(vault_path, "Business")
        self.needs_action_dir = os.path.join(vault_path, "Needs_Action")
        self.inbox_dir = os.path.join(vault_path, "Inbox")

        # Ensure directories exist
        os.makedirs(self.cross_domain_dir, exist_ok=True)
        os.makedirs(self.personal_dir, exist_ok=True)
        os.makedirs(self.business_dir, exist_ok=True)

    def integrate_personal_business(self):
        """Integrate personal and business operations."""
        try:
            # Look for personal communications that might affect business
            personal_items = self._scan_personal_domain()
            business_items = self._scan_business_domain()

            # Find integration opportunities
            integration_opportunities = self._find_integration_opportunities(personal_items, business_items)

            # Create integration plans
            self._create_integration_plans(integration_opportunities)

            logger.info(f"[OK] Cross-domain integration check completed. Found {len(integration_opportunities)} opportunities")
            return True

        except Exception as e:
            logger.error(f"[ERROR] Error in cross-domain integration: {e}")
            return False

    def _scan_personal_domain(self) -> List[Dict[str, Any]]:
        """Scan personal domain for items that could affect business."""
        items = []

        # Check Gmail for business-related communications
        for file in os.listdir(self.needs_action_dir):
            if "GMAIL" in file and any(word in file.lower() for word in ["business", "sale", "client", "customer", "payment"]):
                items.append({
                    "type": "gmail_business",
                    "file": file,
                    "timestamp": datetime.now().isoformat()
                })

        # Check WhatsApp for business-related messages
        # For now, we'll just simulate finding some items
        items.append({
            "type": "whatsapp_business",
            "content": "Potential business inquiry received",
            "timestamp": datetime.now().isoformat()
        })

        return items

    def _scan_business_domain(self) -> List[Dict[str, Any]]:
        """Scan business domain for operations."""
        items = []

        # Check LinkedIn posts
        posted_dir = os.path.join(self.vault_path, "Posted")
        if os.path.exists(posted_dir):
            for file in os.listdir(posted_dir):
                if file.startswith("posted_"):
                    items.append({
                        "type": "linkedin_post",
                        "file": file,
                        "timestamp": datetime.now().isoformat()
                    })

        # Check social media
        social_media_dir = os.path.join(self.vault_path, "Social_Media")
        if os.path.exists(social_media_dir):
            for file in os.listdir(social_media_dir):
                if "summary" in file:
                    items.append({
                        "type": "social_media_summary",
                        "file": file,
                        "timestamp": datetime.now().isoformat()
                    })

        return items

    def _find_integration_opportunities(self, personal_items: List[Dict], business_items: List[Dict]) -> List[Dict[str, Any]]:
        """Find opportunities to integrate personal and business operations."""
        opportunities = []

        for p_item in personal_items:
            for b_item in business_items:
                # Look for related items that could benefit from integration
                if (p_item["type"] == "gmail_business" and b_item["type"] == "linkedin_post"):
                    opportunities.append({
                        "type": "gmail_to_linkedin",
                        "personal_item": p_item,
                        "business_item": b_item,
                        "action": "Follow up on business inquiry with LinkedIn post",
                        "priority": "high"
                    })

        # Add other integration opportunities
        opportunities.append({
            "type": "personal_business_sync",
            "description": "Sync personal contacts with business CRM",
            "action": "Export personal contacts to business domain",
            "priority": "medium"
        })

        opportunities.append({
            "type": "calendar_integration",
            "description": "Sync personal and business calendars",
            "action": "Check for scheduling conflicts between personal and business events",
            "priority": "medium"
        })

        return opportunities

    def _create_integration_plans(self, opportunities: List[Dict[str, Any]]):
        """Create integration plans for identified opportunities."""
        for opportunity in opportunities:
            plan_file = os.path.join(self.cross_domain_dir, f"integration_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{opportunity['type']}.json")

            plan_data = {
                "opportunity": opportunity,
                "created_at": datetime.now().isoformat(),
                "status": "planned",
                "next_steps": [
                    "Review opportunity details",
                    "Create specific action items",
                    "Assign to appropriate system",
                    "Monitor completion"
                ]
            }

            with open(plan_file, 'w') as f:
                json.dump(plan_data, f, indent=2)

            logger.info(f"[OK] Integration plan created: {plan_file}")

    def create_cross_domain_plan(self, task_description: str) -> str:
        """Create a plan that spans multiple domains."""
        plan_file = os.path.join(self.cross_domain_dir, f"cross_domain_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")

        plan_content = f"""# Cross-Domain Plan - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Task
{task_description}

## Domain Analysis
### Personal Domain Impact
- Communications: Gmail, WhatsApp
- Activities: Personal appointments, contacts
- Resources: Personal time, skills

### Business Domain Impact
- Operations: LinkedIn, social media, marketing
- Resources: Business tools, systems
- Objectives: Revenue generation, client acquisition

## Cross-Domain Considerations
- Time allocation between personal and business
- Resource sharing between domains
- Potential conflicts and resolutions

## Execution Steps
1. Analyze task requirements across both domains
2. Identify dependencies between personal and business operations
3. Execute coordinated actions in both domains
4. Sync results and outcomes between domains
5. Generate cross-domain performance report

## Success Metrics
- Task completion in both domains
- Resource optimization
- Efficiency improvements
- Conflict resolution

## Status
- Task: {task_description}
- Status: Planned
- Started: {datetime.now().isoformat()}
- Domain Integration: Active

## Monitoring
- Track progress in both personal and business domains
- Monitor resource allocation
- Check for domain conflicts
- Generate integrated reports
"""

        with open(plan_file, 'w') as f:
            f.write(plan_content)

        logger.info(f"[OK] Cross-domain plan created: {plan_file}")
        return plan_file

    def run_single_check(self):
        """Run single check for cross-domain integration."""
        logger.info("Running cross-domain integration check...")
        success = self.integrate_personal_business()
        logger.info(f"[OK] Cross-domain integration check completed: {'Success' if success else 'Failed'}")
        return success

if __name__ == "__main__":
    # For testing
    cross_integrator = CrossDomainIntegrator()
    success = cross_integrator.integrate_personal_business()
    if success:
        print("[OK] Cross-domain integration completed successfully")
    else:
        print("[ERROR] Cross-domain integration failed")