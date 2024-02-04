"""Test EC2 Instance CDK construct module."""

from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_iam as iam
from aws_cdk.aws_ec2 import IMachineImage
from constructs import Construct


class EC2Construct(Construct):
    """Test EC2 Instance CDK construct class."""

    def __init__(
        self,
        scope: Construct,
        id: str,
        vpc: ec2.IVpc,
        instance_security_group: ec2.SecurityGroup,
        key_name: str,
        *,
        prefix=None,
    ) -> None:
        """Construct initialization."""
        super().__init__(scope, id)

        amzn_linux: IMachineImage = ec2.MachineImage.latest_amazon_linux2(
            edition=ec2.AmazonLinuxEdition.STANDARD,
            virtualization=ec2.AmazonLinuxVirt.HVM,
            storage=ec2.AmazonLinuxStorage.GENERAL_PURPOSE,
        )

        # Instance Role and SSM Managed Policy
        role = iam.Role(
            self,
            "EC2RoleForZeroTrustDemo",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
        )

        role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "AmazonSSMManagedInstanceCore"
            )
        )

        # Instance
        self.instance = ec2.Instance(
            self,
            "DemoPrivateSubnetInstance",
            instance_type=ec2.InstanceType("t3.medium"),
            machine_image=amzn_linux,
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
            ),
            security_group=instance_security_group,
            role=role,
            key_name=key_name,
            require_imdsv2=True,
        )
