"""Main module for CDK application."""

# !/usr/bin/env python3
import aws_cdk as cdk

from cdk.secure_db_connection_service.secure_db_connection_stack import (
    SecureDbConnectionStack,
)

app = cdk.App()
SecureDbConnectionStack(
    app,
    "SecureDbConnectionStack",
)

app.synth()
