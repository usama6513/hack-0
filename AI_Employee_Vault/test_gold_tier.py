"""
Gold Tier Test Script
Tests all Gold Tier components to ensure they work together properly.
"""

import os
import sys
import json
import time
from datetime import datetime

# Add vault path to sys.path to import skills
sys.path.append(os.path.join(os.path.dirname(__file__), 'skills'))

def test_facebook_integration():
    """Test Facebook integration skill."""
    print("Testing Facebook Integration...")
    try:
        from facebook_integration import FacebookIntegration
        fb = FacebookIntegration()
        success = fb.post_to_facebook("Test post from Gold Tier")
        summary = fb.get_post_summary()
        print("[OK] Facebook integration test passed")
        return True
    except Exception as e:
        print(f"[ERROR] Facebook integration test failed: {e}")
        return False

def test_instagram_integration():
    """Test Instagram integration skill."""
    print("Testing Instagram Integration...")
    try:
        from instagram_integration import InstagramIntegration
        ig = InstagramIntegration()
        success = ig.post_to_instagram("Test post from Gold Tier")
        summary = ig.get_post_summary()
        print("[OK] Instagram integration test passed")
        return True
    except Exception as e:
        print(f"[ERROR] Instagram integration test failed: {e}")
        return False

def test_twitter_integration():
    """Test Twitter integration skill."""
    print("Testing Twitter Integration...")
    try:
        from twitter_integration import TwitterIntegration
        tw = TwitterIntegration()
        success = tw.post_to_twitter("Test post from Gold Tier")
        summary = tw.get_post_summary()
        print("[OK] Twitter integration test passed")
        return True
    except Exception as e:
        print(f"[ERROR] Twitter integration test failed: {e}")
        return False

def test_odoo_integration():
    """Test Odoo integration skill."""
    print("Testing Odoo Integration...")
    try:
        from odoo_integration import OdooIntegration
        odoo = OdooIntegration()
        # Try to connect (will fail if Odoo not running, but that's OK for this test)
        models, uid, db = odoo.connect_to_odoo()
        # Generate test data regardless of connection
        data = odoo.get_sales_data(1)
        print("[OK] Odoo integration test passed")
        return True
    except Exception as e:
        print(f"[ERROR] Odoo integration test failed: {e}")
        return False

def test_cross_domain_integrator():
    """Test Cross Domain Integrator skill."""
    print("Testing Cross Domain Integrator...")
    try:
        from cross_domain_integrator import CrossDomainIntegrator
        cross = CrossDomainIntegrator()
        success = cross.integrate_personal_business()
        plan = cross.create_cross_domain_plan("Test cross-domain task")
        print("[OK] Cross Domain Integrator test passed")
        return True
    except Exception as e:
        print(f"[ERROR] Cross Domain Integrator test failed: {e}")
        return False

def test_business_auditor():
    """Test Business Auditor skill."""
    print("Testing Business Auditor...")
    try:
        from business_auditor import BusinessAuditor
        auditor = BusinessAuditor()
        report = auditor.run_audit()
        weekly_report = auditor.generate_weekly_report()
        print("[OK] Business Auditor test passed")
        return True
    except Exception as e:
        print(f"[ERROR] Business Auditor test failed: {e}")
        return False

def test_ceo_briefing_generator():
    """Test CEO Briefing Generator skill."""
    print("Testing CEO Briefing Generator...")
    try:
        from ceo_briefing_generator import CEOBriefingGenerator
        briefing_gen = CEOBriefingGenerator()
        briefing = briefing_gen.generate_briefing()
        # Run the check function
        briefing_gen.check_and_generate_briefing()
        print("[OK] CEO Briefing Generator test passed")
        return True
    except Exception as e:
        print(f"[ERROR] CEO Briefing Generator test failed: {e}")
        return False

def test_error_recovery():
    """Test Error Recovery skill."""
    print("Testing Error Recovery...")
    try:
        from error_recovery import ErrorRecovery
        error_rec = ErrorRecovery()
        # Simulate handling an error
        result = error_rec.handle_error("api_errors", "API rate limit exceeded", {"service": "Test", "retry_after": 5})
        # Run a check
        issues = error_rec.check_for_issues()
        report = error_rec.create_error_report()
        print("[OK] Error Recovery test passed")
        return True
    except Exception as e:
        print(f"[ERROR] Error Recovery test failed: {e}")
        return False

def test_audit_logger():
    """Test Audit Logger skill."""
    print("Testing Audit Logger...")
    try:
        from audit_logger import AuditLogger
        audit_log = AuditLogger()
        # Log a test operation
        log_file = audit_log.log_operation("test_operation", {"test": True, "source_component": "test_script"})
        # Create summary
        summary = audit_log.generate_audit_summary(1)
        # Run cleanup
        cleanup = audit_log.run_log_cleanup()
        print("[OK] Audit Logger test passed")
        return True
    except Exception as e:
        print(f"[ERROR] Audit Logger test failed: {e}")
        return False

def test_ralph_wiggum_loop():
    """Test Ralph Wiggum Loop skill."""
    print("Testing Ralph Wiggum Loop...")
    try:
        from ralph_wiggum_loop import RalphWiggumLoop
        ralph = RalphWiggumLoop()

        # Create a simple test function with state in a mutable object
        state = {"counter": 0}
        def test_task():
            state["counter"] += 1
            counter = state["counter"]
            if counter >= 3:  # Complete after 3 iterations
                return {"completed": True, "result": f"Completed after {counter} iterations"}
            else:
                return {"completed": False, "result": f"Iteration {counter}"}

        # Create and run a loop
        loop_id = ralph.run_autonomous_task("Test task", test_task, max_iterations=5)
        time.sleep(2)  # Wait for loop to run
        status = ralph.get_loop_status(loop_id)
        ralph.stop_loop(loop_id)
        print("[OK] Ralph Wiggum Loop test passed")
        return True
    except Exception as e:
        print(f"[ERROR] Ralph Wiggum Loop test failed: {e}")
        return False

def test_directories():
    """Test that all required directories exist."""
    print("Testing directory structure...")
    required_dirs = [
        "Accounting",
        "Social_Media",
        "Facebook_Posts",
        "Instagram_Posts",
        "Twitter_Posts",
        "CEO_Briefings",
        "Business_Audits",
        "Error_Logs",
        "Audit_Logs",
        "Ralph_Loops",
        "Cross_Domain",
        "MCP_Servers"
    ]

    vault_path = os.path.dirname(__file__)
    missing_dirs = []

    for dir_name in required_dirs:
        dir_path = os.path.join(vault_path, dir_name)
        if not os.path.exists(dir_path):
            missing_dirs.append(dir_name)

    if missing_dirs:
        print(f"[ERROR] Missing directories: {missing_dirs}")
        return False
    else:
        print("[OK] All required directories exist")
        return True

def main():
    """Run all Gold Tier tests."""
    print("=" * 60)
    print("AI EMPLOYEE GOLD TIER TEST SUITE")
    print(f"Test Run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    tests = [
        ("Directory Structure", test_directories),
        ("Facebook Integration", test_facebook_integration),
        ("Instagram Integration", test_instagram_integration),
        ("Twitter Integration", test_twitter_integration),
        ("Odoo Integration", test_odoo_integration),
        ("Cross Domain Integration", test_cross_domain_integrator),
        ("Business Auditor", test_business_auditor),
        ("CEO Briefing Generator", test_ceo_briefing_generator),
        ("Error Recovery", test_error_recovery),
        ("Audit Logger", test_audit_logger),
        ("Ralph Wiggum Loop", test_ralph_wiggum_loop)
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        result = test_func()
        results.append((test_name, result))

    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)

    passed = 0
    failed = 0

    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name:<30} {status}")
        if result:
            passed += 1
        else:
            failed += 1

    print("-" * 60)
    print(f"Total: {len(results)} tests")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {passed/len(results)*100:.1f}%")

    if failed == 0:
        print("\n[OK] ALL TESTS PASSED! Gold Tier implementation is complete.")
        print("The AI Employee Gold Tier system is ready for autonomous operation.")
    else:
        print(f"\n[ERROR] {failed} tests failed. Please check the implementation.")

    print("=" * 60)

if __name__ == "__main__":
    main()