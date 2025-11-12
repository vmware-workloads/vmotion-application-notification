#!/usr/bin/env python3
"""
Convenience script to run all tests from the project root
"""
import sys
import os

# Add the project directory to the path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Import and run the test suite
from tests.test_all import run_tests

if __name__ == '__main__':
    # Check for verbosity argument
    verbosity = 2
    if len(sys.argv) > 1:
        if sys.argv[1] == '-v':
            verbosity = 2
        elif sys.argv[1] == '-q':
            verbosity = 0
    
    sys.exit(run_tests(verbosity))

