#!/usr/bin/env python3
"""
Auto-generate XML and CSV files for the daschland-scripts project.

This script is used in GitHub Actions to automatically generate the XML and CSV files
when a PR is opened or updated, ensuring they stay in sync with the Python code.
"""

import os
import sys
import warnings

from dsp_tools.error.xmllib_warnings import XmllibInputInfo
from src.xmllib.xmllib_main import main

ENV_VARS = ["XMLLIB_SORT_RESOURCES", "XMLLIB_SORT_PROPERTIES", "XMLLIB_AUTHORSHIP_ID_WITH_INTEGERS"]


def generate_files() -> None:
    """Generate XML and CSV files with the appropriate environment variables set."""
    # Set environment variables for consistent, reproducible generation
    for env_var in ENV_VARS:
        os.environ[env_var] = "true"

    # Suppress informational warnings during generation
    with warnings.catch_warnings():
        warnings.simplefilter(action="ignore", category=XmllibInputInfo)
        main()

    print("✓ Successfully generated XML and CSV files")


if __name__ == "__main__":
    try:
        generate_files()
        sys.exit(0)
    except Exception as e:  # noqa: BLE001 (broad exception is appropriate for CI/CD utility script)
        print(f"✗ Error generating files: {e}", file=sys.stderr)
        sys.exit(1)
