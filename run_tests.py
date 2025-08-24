#!/usr/bin/env python3
"""
Test runner script for Sales Analytics application.
Run different types of tests with various options.
"""

import subprocess
import sys
import argparse
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}\n")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        print(f"\n✅ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {description} failed with exit code {e.returncode}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Run tests for Sales Analytics application")
    parser.add_argument(
        "--type", 
        choices=["unit", "integration", "all", "coverage", "lint"],
        default="all",
        help="Type of tests to run"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Run only fast tests (skip slow/AI tests)"
    )
    
    args = parser.parse_args()
    
    # Base pytest command
    base_cmd = ["python", "-m", "pytest"]
    
    if args.verbose:
        base_cmd.append("-v")
    
    # Add markers based on test type
    if args.type == "unit":
        cmd = base_cmd + ["-m", "not integration and not slow"]
    elif args.type == "integration":
        cmd = base_cmd + ["-m", "integration"]
    elif args.type == "coverage":
        cmd = base_cmd + ["--cov=app", "--cov-report=html", "--cov-report=term-missing"]
    elif args.type == "lint":
        # Run linting instead of tests
        success = True
        success &= run_command(["python", "-m", "black", "--check", "app", "tests"], "Black code formatting check")
        success &= run_command(["python", "-m", "isort", "--check-only", "app", "tests"], "Import sorting check")
        success &= run_command(["python", "-m", "mypy", "app"], "Type checking with mypy")
        return 0 if success else 1
    else:  # all
        if args.fast:
            cmd = base_cmd + ["-m", "not slow"]
        else:
            cmd = base_cmd
    
    # Run the tests
    success = run_command(cmd, f"Running {args.type} tests")
    
    if success:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n💥 Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
