"""
Business Auditor Skill for AI Employee - Gold Tier
Audits business operations and generates accounting reports.
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
        logging.FileHandler('business_auditor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BusinessAuditor:
    """
    Skill to audit business operations and generate accounting reports.
    """

    def __init__(self, vault_path="./"):
        self.vault_path = vault_path
        self.audit_dir = os.path.join(vault_path, "Business_Audits")
        self.accounting_dir = os.path.join(vault_path, "Accounting")
        self.posted_dir = os.path.join(vault_path, "Posted")
        self.needs_action_dir = os.path.join(vault_path, "Needs_Action")
        self.sent_dir = os.path.join(vault_path, "Sent")

        # Ensure directories exist
        os.makedirs(self.audit_dir, exist_ok=True)
        os.makedirs(self.accounting_dir, exist_ok=True)

    def run_audit(self) -> Dict[str, Any]:
        """Run comprehensive business audit."""
        try:
            # Collect all business metrics
            metrics = self._collect_business_metrics()

            # Generate audit report
            audit_report = self._generate_audit_report(metrics)

            # Save audit report
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            audit_file = os.path.join(self.audit_dir, f"business_audit_{timestamp}.json")

            with open(audit_file, 'w') as f:
                json.dump(audit_report, f, indent=2, default=str)

            logger.info(f"[OK] Business audit completed: {audit_file}")
            return audit_report

        except Exception as e:
            logger.error(f"[ERROR] Error running business audit: {e}")
            return {}

    def _collect_business_metrics(self) -> Dict[str, Any]:
        """Collect business metrics from various sources."""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "social_media": self._collect_social_media_metrics(),
            "communications": self._collect_communication_metrics(),
            "revenue_activities": self._collect_revenue_metrics(),
            "automated_tasks": self._collect_task_metrics(),
            "accounting_data": self._collect_accounting_metrics()
        }
        return metrics

    def _collect_social_media_metrics(self) -> Dict[str, int]:
        """Collect social media metrics."""
        linkedin_posts = 0
        if os.path.exists(self.posted_dir):
            linkedin_posts = len([f for f in os.listdir(self.posted_dir) if f.startswith("posted_")])

        # Look for social media directories
        social_dirs = ["Facebook_Posts", "Instagram_Posts", "Twitter_Posts"]
        social_metrics = {"linkedin_posts": linkedin_posts}

        for social_dir in social_dirs:
            full_path = os.path.join(self.vault_path, social_dir)
            if os.path.exists(full_path):
                posts = len([f for f in os.listdir(full_path) if f.startswith(f"{social_dir.lower().replace('_posts', '')}_post")])
                social_metrics[f"{social_dir.lower().replace('_posts', '')}_posts"] = posts

        return social_metrics

    def _collect_communication_metrics(self) -> Dict[str, int]:
        """Collect communication metrics."""
        gmail_items = 0
        if os.path.exists(self.needs_action_dir):
            gmail_items = len([f for f in os.listdir(self.needs_action_dir) if "GMAIL" in f])

        whatsapp_items = 0  # Would need to check WhatsApp messages

        emails_sent = 0
        if os.path.exists(self.sent_dir):
            emails_sent = len(os.listdir(self.sent_dir))

        return {
            "gmail_processed": gmail_items,
            "emails_sent": emails_sent,
            "whatsapp_messages": whatsapp_items
        }

    def _collect_revenue_metrics(self) -> Dict[str, Any]:
        """Collect revenue-related metrics."""
        # For now, we'll simulate some basic metrics
        return {
            "potential_leads": 0,  # Would need to analyze communications for leads
            "follow_ups_pending": 0,  # Would need to track follow-ups
            "revenue_generating_content": 0  # Would need to track content that generates revenue
        }

    def _collect_task_metrics(self) -> Dict[str, int]:
        """Collect automated task metrics."""
        plans_dir = os.path.join(self.vault_path, "Plans")
        needs_action_items = 0
        if os.path.exists(plans_dir):
            needs_action_items = len(os.listdir(plans_dir))

        return {
            "plans_created": needs_action_items,
            "tasks_automated": 0,  # Would need to track completed tasks
            "tasks_pending": 0  # Would need to track pending tasks
        }

    def _collect_accounting_metrics(self) -> Dict[str, Any]:
        """Collect accounting metrics."""
        if os.path.exists(self.accounting_dir):
            # Get the most recent accounting data
            files = [f for f in os.listdir(self.accounting_dir) if f.startswith("odoo_")]
            return {
                "accounting_files": len(files),
                "recent_syncs": len([f for f in files if "sales_data" in f])
            }
        return {
            "accounting_files": 0,
            "recent_syncs": 0
        }

    def _generate_audit_report(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive audit report."""
        report = {
            "audit_type": "comprehensive_business_audit",
            "timestamp": metrics["timestamp"],
            "summary": {
                "total_social_media_posts": sum(metrics["social_media"].values()),
                "total_communications_handled": sum(metrics["communications"].values()),
                "automated_tasks_tracked": sum(metrics["automated_tasks"].values())
            },
            "detailed_metrics": metrics,
            "insights": self._generate_insights(metrics),
            "recommendations": self._generate_recommendations(metrics),
            "status": "completed"
        }
        return report

    def _generate_insights(self, metrics: Dict[str, Any]) -> List[str]:
        """Generate business insights from metrics."""
        insights = []

        # Social media insights
        total_posts = sum(metrics["social_media"].values())
        if total_posts > 0:
            insights.append(f"Total social media posts: {total_posts}")
            if total_posts > 10:
                insights.append("High social media activity - consider optimizing posting schedule")
            else:
                insights.append("Low social media activity - consider increasing content generation")

        # Communication insights
        total_communications = sum(metrics["communications"].values())
        if total_communications > 0:
            insights.append(f"Total communications handled: {total_communications}")
            if total_communications > 50:
                insights.append("High communication volume - automation is effective")

        # Task automation insights
        if metrics["automated_tasks"]["tasks_automated"] > 0:
            insights.append(f"Tasks automated: {metrics['automated_tasks']['tasks_automated']}")

        return insights

    def _generate_recommendations(self, metrics: Dict[str, Any]) -> List[str]:
        """Generate business recommendations from metrics."""
        recommendations = []

        # If social media activity is low
        total_posts = sum(metrics["social_media"].values())
        if total_posts < 5:
            recommendations.append("Increase social media posting frequency to improve engagement")

        # If communication volume is high
        total_communications = sum(metrics["communications"].values())
        if total_communications > 100:
            recommendations.append("Consider implementing more sophisticated communication categorization")

        # If accounting integration exists
        if metrics["accounting_data"]["accounting_files"] > 0:
            recommendations.append("Accounting integration is active, continue monitoring for business insights")

        # General recommendations
        recommendations.append("Continue monitoring business metrics for optimization opportunities")
        recommendations.append("Regularly review and update automation workflows")

        return recommendations

    def generate_weekly_report(self) -> str:
        """Generate weekly business report."""
        audit_report = self.run_audit()

        report_file = os.path.join(self.audit_dir, f"weekly_business_report_{datetime.now().strftime('%Y%m%d')}.md")

        report_content = f"""# Weekly Business Report - {datetime.now().strftime('%Y-%m-%d')}

## Executive Summary
This report provides an overview of business operations for the week ending {datetime.now().strftime('%Y-%m-%d')}.

## Key Metrics
- **Total Social Media Posts:** {audit_report['summary']['total_social_media_posts']}
- **Communications Handled:** {audit_report['summary']['total_communications_handled']}
- **Tasks Automated:** {audit_report['summary']['automated_tasks_tracked']}

## Social Media Activity
{self._format_social_media_report(audit_report['detailed_metrics']['social_media'])}

## Communication Overview
{self._format_communication_report(audit_report['detailed_metrics']['communications'])}

## Insights
{chr(10).join([f"- {insight}" for insight in audit_report['insights']])}

## Recommendations
{chr(10).join([f"- {rec}" for rec in audit_report['recommendations']])}

## Next Week's Focus
- Continue current automation strategies
- Monitor the effectiveness of recommendations
- Look for new automation opportunities

---
*Report generated by AI Employee Business Auditor*
*Generated at: {audit_report['timestamp']}*
"""

        with open(report_file, 'w') as f:
            f.write(report_content)

        logger.info(f"[OK] Weekly business report generated: {report_file}")
        return report_file

    def _format_social_media_report(self, metrics: Dict[str, int]) -> str:
        """Format social media metrics for report."""
        lines = []
        for platform, count in metrics.items():
            platform_name = platform.replace('_posts', '').replace('_', ' ').title()
            lines.append(f"  - {platform_name}: {count} posts")
        return '\n'.join(lines)

    def _format_communication_report(self, metrics: Dict[str, int]) -> str:
        """Format communication metrics for report."""
        lines = []
        for comm_type, count in metrics.items():
            type_name = comm_type.replace('_', ' ').title()
            lines.append(f"  - {type_name}: {count} items")
        return '\n'.join(lines)

    def run_single_check(self):
        """Run single check for business auditing."""
        logger.info("Running business audit check...")
        report = self.run_audit()
        logger.info(f"[OK] Business audit completed. Metrics collected: {len(report.get('detailed_metrics', {}))}")
        return True

if __name__ == "__main__":
    # For testing
    auditor = BusinessAuditor()
    report = auditor.run_audit()
    if report:
        print(f"[OK] Business audit completed with {len(report.get('insights', []))} insights")

        # Generate weekly report
        weekly_report = auditor.generate_weekly_report()
        print(f"[OK] Weekly report generated: {weekly_report}")
    else:
        print("[ERROR] Business audit failed")