"""CDK Stack test module."""

import aws_cdk as core
import aws_cdk.assertions as assertions

from cdk.secure_db_connection_service.secure_db_connection_stack import (
    SecureDbConnectionStack,
)


# example tests. To run these tests, uncomment this file along with the example
# resource in secure_db_connection/secure_db_connection_stack.py
def test_sqs_queue_created():
    """Test case: does the synthesized stack have a SQS queue."""
    app = core.App()
    stack = SecureDbConnectionStack(app, "secure-db-connection")
    template = assertions.Template.from_stack(stack)  # noqa: F841


#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
