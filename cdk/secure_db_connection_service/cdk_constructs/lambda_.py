"""Initialization Lambda CDK construct module."""

import aws_cdk as cdk
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as lambda_
from aws_cdk import aws_lambda_python_alpha as lambda_python
from aws_cdk import aws_logs as logs
from aws_cdk import aws_secretsmanager as sme
from aws_cdk import custom_resources as cr
from cdk_constructs.constants import IAM_DB_USER
from constructs import Construct


class LambdaConstruct(Construct):
    """Initialization Lambda CDK construct class."""

    def __init__(
        self,
        scope: Construct,
        id: str,
        vpc: ec2.IVpc,
        init_lambda_security_group: ec2.ISecurityGroup,
        db_secret: sme.ISecret,
        *,
        prefix=None,
    ):
        """Construct initialization."""
        super().__init__(scope, id)

        rds_init_function = lambda_python.PythonFunction(
            self,
            "RDSInitFunction",
            entry="cdk/lambdas/rds_init",
            runtime=lambda_.Runtime.PYTHON_3_8,
            index="index.py",
            handler="lambda_handler",
            timeout=cdk.Duration.seconds(amount=30),
            log_retention=logs.RetentionDays.ONE_WEEK,
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
            ),
            security_groups=[init_lambda_security_group],
        )

        rds_init_function.add_to_role_policy(
            statement=iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["secretsmanager:GetSecretValue"],
                resources=[db_secret.secret_arn],
            )
        )

        rds_init_resource_provider = cr.Provider(
            self, "RDSInitCRProvider", on_event_handler=rds_init_function
        )

        rds_init_resource = cdk.CustomResource(  # noqa: F841
            self,
            "RDSInitResource",
            properties={"DBSecretArn": db_secret.secret_arn, "IAMDBUser": IAM_DB_USER},
            removal_policy=cdk.RemovalPolicy.DESTROY,
            resource_type="Custom::IAMDBUser",
            service_token=rds_init_resource_provider.service_token,
        )
