#!/usr/bin/env python3
import argparse
import subprocess
import os
import sys

def run_tests(test_type="all", verbose=False):
    """
    Run the specified tests.
    
    Args:
        test_type: Type of tests to run ('unit', 'integration', or 'all')
        verbose: Whether to show verbose output
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Ensure services are running before tests (you'll need to have docker-compose up first)
    print("Make sure all microservices are running before running tests.")
    print("Run 'docker compose up' in a separate terminal if they're not already running.")
    
    # Build the pytest command
    pytest_cmd = ["pytest", "-v"] if verbose else ["pytest"]
    
    if test_type == "unit":
        pytest_cmd.append("tests/unit/")
    elif test_type == "integration":
        pytest_cmd.append("tests/integration/")
    else:  # all
        pytest_cmd.append("tests/")
    
    # Add coverage reporting
    pytest_cmd.extend(["--cov=.", "--cov-report=term"])
    
    print(f"Running {test_type} tests...")
    result = subprocess.run(pytest_cmd, cwd=base_dir)
    
    return result.returncode

def main():
    """Main entry point for the test runner."""
    parser = argparse.ArgumentParser(description="Run tests for the Virtual Labs microservices")
    parser.add_argument("--type", choices=["unit", "integration", "all"], 
                        default="all", help="Type of tests to run")
    parser.add_argument("--verbose", action="store_true", help="Show verbose output")
    
    args = parser.parse_args()
    
    sys.exit(run_tests(args.type, args.verbose))

if __name__ == "__main__":
    main()