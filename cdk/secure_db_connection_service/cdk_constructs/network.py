"""Network CDK construct module."""

import aws_cdk as cdk
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_logs as logs
from aws_cdk import custom_resources as cr
from constructs import Construct


class NetworkConstruct(Construct):
    """Network CDK construct class."""

    def __init__(self, scope: Construct, id: str, *, prefix=None):
        """Construct initialization."""
        super().__init__(scope, id)

        network_vpc = ec2.Vpc(
            self,
            "Vpc",
            max_azs=2,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Subnet1",
                    cidr_mask=24,
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                ),
            ],
        )

        vpc_endpoint_sg = ec2.SecurityGroup(
            self, "VPCEndpointSG", vpc=network_vpc, allow_all_outbound=False
        )

        db_sg = ec2.SecurityGroup(
            self,
            "DBSG",
            vpc=network_vpc,
            description="DB security group",
            allow_all_outbound=False,
        )

        container_sg = ec2.SecurityGroup(
            self,
            "ContainerSG",
            vpc=network_vpc,
            description="ECS Container security group",
            allow_all_outbound=False,
        )

        init_lambda_security_group = ec2.SecurityGroup(
            self,
            "InitLambdaSG",
            vpc=network_vpc,
            description="Initialization Lambda Security Group",
            allow_all_outbound=False,
        )

        network_vpc.add_gateway_endpoint(
            "S3VPCEndpoint",
            service=ec2.GatewayVpcEndpointAwsService.S3,
            subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
            ).subnets,
        )

        s3_prefix_list_cr = cr.AwsCustomResource(
            self,
            "S3PrefixListCR",
            on_update=cr.AwsSdkCall(
                service="EC2",
                action="describePrefixLists",
                parameters={
                    "Filters": [
                        {
                            "Name": "prefix-list-name",
                            "Values": [f"com.amazonaws.{cdk.Stack.of(self).region}.s3"],
                        }
                    ]
                },
                physical_resource_id=cr.PhysicalResourceId.from_response(
                    response_path="PrefixLists.0.PrefixListId"
                ),
            ),
            policy=cr.AwsCustomResourcePolicy.from_sdk_calls(
                resources=cr.AwsCustomResourcePolicy.ANY_RESOURCE
            ),
            log_retention=logs.RetentionDays.ONE_WEEK,
        )

        s3_prefix_list_id = s3_prefix_list_cr.get_response_field(
            "PrefixLists.0.PrefixListId"
        )

        for service in ["ssmmessages", "ecr.api", "ecr.dkr", "logs", "secretsmanager"]:
            network_vpc.add_interface_endpoint(
                f"{service.capitalize()}VPCEndpoint",
                service=ec2.InterfaceVpcEndpointAwsService(name=service, port=443),
                private_dns_enabled=True,
                subnets=ec2.SubnetSelection(
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
                ),
                security_groups=[vpc_endpoint_sg],
            )

        init_lambda_security_group.connections.allow_to(
            db_sg, ec2.Port.tcp(3306), "Allow traffic from initialization lambda to db"
        )
        init_lambda_security_group.connections.allow_to(
            vpc_endpoint_sg,
            ec2.Port.tcp(443),
            "Allow traffic from initialization lambda to interface vpc endpoints",
        )

        container_sg.connections.allow_to(
            db_sg, ec2.Port.tcp(3306), "Allow traffic from container to db"
        )
        container_sg.add_egress_rule(
            peer=ec2.Peer.prefix_list(prefix_list_id=s3_prefix_list_id),
            connection=ec2.Port.tcp(443),
            description="Allow traffic from container to s3 gateway endpoint",
        )
        container_sg.connections.allow_to(
            vpc_endpoint_sg,
            ec2.Port.tcp(443),
            "Allow traffic from container to interface vpc endpoints",
        )
        
        ec2_instacnce_sg = ec2.SecurityGroup(
            self, "DemoInstanceSecurityGroup",
            vpc=network_vpc,
            allow_all_outbound=False 
        )

        # Allow inbound SSH access (you can customize the rules as needed)
        ec2_instacnce_sg.add_ingress_rule(
            container_sg,
            ec2.Port.tcp(22),
            "Allow SSH Access"
        )

        container_sg.add_egress_rule(
            ec2_instacnce_sg,
            connection=ec2.Port.tcp(22),
            description="Allow traffic from container to ec2 instance",
        )

        self.vpc = network_vpc
        self.db_sg = db_sg
        self.init_lambda_security_group = init_lambda_security_group
        self.container_sg = container_sg
        self.ec2_instacnce_sg = ec2_instacnce_sg
