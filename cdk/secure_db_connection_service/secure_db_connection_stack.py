"""CDK Stack module."""

from aws_cdk import Stack
from cdk_constructs.containers import ContainersConstruct
from cdk_constructs.ec2 import EC2Construct
from cdk_constructs.db import DBConstruct
from cdk_constructs.lambda_ import LambdaConstruct
from cdk_constructs.network import NetworkConstruct
from constructs import Construct


class SecureDbConnectionStack(Stack):
    """CDK Stack class."""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        """Stack initialization."""
        super().__init__(scope, construct_id, **kwargs)

        network_construct = NetworkConstruct(self, "NetworkConstruct")

        db_construct = DBConstruct(
            self,
            "DBConstruct",
            vpc=network_construct.vpc,
            security_group=network_construct.db_sg,
        )

        lambda_construct = LambdaConstruct(  # noqa: F841
            self,
            "LambdaConstruct",
            vpc=network_construct.vpc,
            init_lambda_security_group=network_construct.init_lambda_security_group,
            db_secret=db_construct.db_secret,
        )

        containers_construct = ContainersConstruct(  # noqa: F841
            self,
            "ContainersConstruct",
            vpc=network_construct.vpc,
            container_security_group=network_construct.container_sg,
        )

        # Declare dependencies

        lambda_construct.node.add_dependency(db_construct)
        containers_construct.node.add_dependency(lambda_construct)

        ec2_construct = EC2Construct(self, "EC2Construct", network_construct.vpc, instance_security_group=network_construct.ec2_instacnce_sg)
        ec2_construct.node.add_dependency(db_construct)
