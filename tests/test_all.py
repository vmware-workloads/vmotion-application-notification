#!/usr/bin/env python3
"""
Test runner for all unit tests
"""
import unittest
import sys
import os

# Add the project directory to the path
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_dir)

# Import all test modules
from tests.test_vmnotification_config import TestVMNotificationConfig
from tests.test_vmnotification_service import TestVMNotificationService, TestVMNotificationServiceIntegration
from tests.test_utils import TestGetLoggingLevel, TestCreateFolders, TestUtilsIntegration
from tests.test_vmnotification_exception import TestVMNotificationException


def create_test_suite():
    """Create a test suite containing all tests"""
    suite = unittest.TestSuite()
    
    # Add config tests
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestVMNotificationConfig))
    
    # Add service tests
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestVMNotificationService))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestVMNotificationServiceIntegration))
    
    # Add utils tests
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestGetLoggingLevel))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCreateFolders))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestUtilsIntegration))
    
    # Add exception tests
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestVMNotificationException))
    
    return suite


def run_tests(verbosity=2):
    """Run all tests with specified verbosity"""
    suite = create_test_suite()
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    print("=" * 70)
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    # Check for verbosity argument
    verbosity = 2
    if len(sys.argv) > 1:
        if sys.argv[1] == '-v':
            verbosity = 2
        elif sys.argv[1] == '-q':
            verbosity = 0
    
    sys.exit(run_tests(verbosity))

