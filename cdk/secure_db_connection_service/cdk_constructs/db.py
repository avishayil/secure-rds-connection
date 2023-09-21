"""Database CDK construct module."""

import json

import aws_cdk as cdk
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_rds as rds
from aws_cdk import aws_secretsmanager as sme
from constructs import Construct

from cdk.secure_db_connection_service.cdk_constructs.constants import (
    CLUSTER_DB_NAME,
    CLUSTER_MASTER_USER_NAME,
    IAM_DB_USER,
)


class DBConstruct(Construct):
    """Database CDK construct class."""

    def __init__(
        self,
        scope: Construct,
        id: str,
        *,
        prefix=None,
        vpc: ec2.IVpc,
        security_group: ec2.ISecurityGroup
    ):
        """Construct initialization."""
        super().__init__(scope, id)

        db_secret = sme.Secret(
            self,
            "DBSecret",
            generate_secret_string=sme.SecretStringGenerator(
                exclude_punctuation=True,
                include_space=False,
                secret_string_template=json.dumps(
                    {
                        "username": CLUSTER_MASTER_USER_NAME,
                    }
                ),
                generate_string_key="password",
            ),
        )

        db = rds.DatabaseCluster(
            self,
            "DB",
            engine=rds.DatabaseClusterEngine.aurora_mysql(
                version=rds.AuroraMysqlEngineVersion.VER_3_02_0
            ),
            storage_encrypted=True,
            iam_authentication=True,
            default_database_name=CLUSTER_DB_NAME,
            credentials=rds.Credentials.from_secret(
                secret=db_secret, username="master"
            ),
            backup=rds.BackupProps(retention=cdk.Duration.days(7)),
            instance_props=rds.InstanceProps(
                instance_type=ec2.InstanceType.of(
                    ec2.InstanceClass.BURSTABLE3, ec2.InstanceSize.MEDIUM
                ),
                vpc_subnets=ec2.SubnetSelection(
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
                ),
                vpc=vpc,
                publicly_accessible=False,
                allow_major_version_upgrade=False,
                auto_minor_version_upgrade=True,
                security_groups=[security_group],
            ),
            deletion_protection=False,
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )

        cdk.CfnOutput(self, "AuroraClusterEndpoint", value=db.cluster_endpoint.hostname)
        cdk.CfnOutput(self, "AuroraDatabaseName", value=CLUSTER_DB_NAME)
        cdk.CfnOutput(self, "AuroraRDSUserName", value=IAM_DB_USER)

        self.db_cluster = db
        self.db_secret = db_secret
