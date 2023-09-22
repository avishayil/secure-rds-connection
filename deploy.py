#!/usr/bin/env python3
"""Deployment script for the parameterized CDK stack."""

import argparse
import subprocess


def main():
    """Main Function."""
    parser = argparse.ArgumentParser(
        description="Deploy CDK stack with a KeyName parameter"
    )
    parser.add_argument(
        "--key-name", required=True, help="The KeyName parameter for the CDK stack"
    )

    args = parser.parse_args()

    # Run the cdk deploy command with the provided KeyName parameter
    try:
        subprocess.run(
            ["cdk", "deploy", "--parameters", f"KeyNameParam={args.key_name}"],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"Error: CDK deploy command failed with exit code {e.returncode}")


if __name__ == "__main__":
    main()
