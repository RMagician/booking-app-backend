"""
Script to run tests with coverage
"""

import os
import sys
import argparse
import pytest
from pathlib import Path


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Run tests for booking app backend"
    )
    parser.add_argument(
        "-k",
        "--filter",
        help="Only run tests that match the given substring expression",
        default=None,
    )
    parser.add_argument(
        "-m",
        "--marker",
        help="Only run tests with the specified marker",
        choices=["unit", "integration", "api", "repository"],
        default=None,
    )
    parser.add_argument(
        "--no-cov",
        help="Disable coverage report",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="Enable verbose output",
        action="store_true",
        default=False,
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    # Set environment variable to use test settings
    os.environ["ENV"] = "test"
    os.environ["MONGODB_DB_NAME"] = "booking_app_test"
    os.environ["MONGODB_URI"] = "mongodb://admin:secret@localhost:27017"

    # Build pytest arguments
    pytest_args = []

    # Add filter if specified
    if args.filter:
        pytest_args.extend(["-k", args.filter])

    # Add marker if specified
    if args.marker:
        pytest_args.extend(["-m", args.marker])

    # Add verbose flag if specified
    if args.verbose:
        pytest_args.append("-v")

    # Add coverage arguments unless disabled
    if not args.no_cov:
        pytest_args.extend(
            ["--cov=app", "--cov-report=term", "--cov-report=html"]
        )

    # Create coverage directory if it doesn't exist
    coverage_dir = Path("coverage_html")
    coverage_dir.mkdir(exist_ok=True)

    # Run the tests
    sys.exit(pytest.main(pytest_args))
