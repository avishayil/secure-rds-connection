"""Containers CDK construct module."""

import aws_cdk as cdk
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecr as ecr
from aws_cdk import aws_ecr_assets as ecr_assets
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_iam as iam
from aws_cdk import aws_logs as logs
from cdk_ecr_deployment import DockerImageName, ECRDeployment
from constructs import Construct


class ContainersConstruct(Construct):
    """Containers CDK construct class."""

    def __init__(
        self,
        scope: Construct,
        id: str,
        *,
        vpc: ec2.IVpc,
        container_security_group: ec2.ISecurityGroup,
    ):
        """Construct initialization."""
        super().__init__(scope, id)

        ecr_repository = ecr.Repository(
            self,
            "ECRRepository",
            encryption=ecr.RepositoryEncryption.AES_256,
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )

        ecr_image = ecr_assets.DockerImageAsset(
            self, "DockerImage", directory="cdk/containers"
        )

        ecr_deployment = ECRDeployment(  # noqa: F841
            self,
            "ECRDeployment",
            src=DockerImageName(name=ecr_image.image_uri),
            dest=DockerImageName(name=ecr_repository.repository_uri),
        )
        ecs_cluster = ecs.Cluster(self, "Cluster", vpc=vpc)

        ecs_task_role = iam.Role(
            self,
            "TaskRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            inline_policies={
                "GenericECSTask": iam.PolicyDocument(
                    assign_sids=True,
                    minimize=True,
                    statements=[
                        iam.PolicyStatement(
                            resources=["*"],
                            actions=[
                                "logs:CreateLogStream",
                                "logs:DescribeLogGroups",
                                "logs:DescribeLogStreams",
                                "logs:CreateLogGroup",
                                "logs:PutLogEvents",
                                "logs:PutRetentionPolicy",
                            ],
                        ),
                        iam.PolicyStatement(
                            resources=["*"], actions=["ec2:DescribeRegions"]
                        ),
                        iam.PolicyStatement(
                            resources=["*"],
                            actions=[
                                "ssmmessages:CreateControlChannel",
                                "ssmmessages:CreateDataChannel",
                                "ssmmessages:OpenControlChannel",
                                "ssmmessages:OpenDataChannel",
                            ],
                        ),
                        iam.PolicyStatement(
                            resources=["*"],
                            actions=[
                                "cloudwatch:PutMetricData",
                                "cloudwatch:ListMetrics",
                            ],
                        ),
                    ],
                )
            },
        )

        ecs_task_execution_role = iam.Role(
            self,
            "TaskExecutionRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_managed_policy_arn(
                    self,
                    "ServiceRole",
                    managed_policy_arn="arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy",
                )
            ],
        )

        ecs_task_definition = ecs.FargateTaskDefinition(
            self,
            "TaskDefinition",
            cpu=512,
            memory_limit_mib=2048,
            execution_role=ecs_task_execution_role,
            task_role=ecs_task_role,
            runtime_platform=ecs.RuntimePlatform(
                operating_system_family=ecs.OperatingSystemFamily.LINUX,
                cpu_architecture=ecs.CpuArchitecture.X86_64
            ),
        )

        ecs_ssm_agent_container = ecs_task_definition.add_container(  # noqa: F841
            "ssm-agent",
            image=ecs.ContainerImage.from_ecr_repository(
                repository=ecr_repository, tag="latest"
            ),
            privileged=False,
            logging=ecs.LogDriver.aws_logs(
                stream_prefix="ContainerLogs-",
                log_retention=logs.RetentionDays.ONE_WEEK,
            ),
        )

        ecs_service = ecs.FargateService(  # noqa: F841
            self,
            "EcsService",
            cluster=ecs_cluster,
            task_definition=ecs_task_definition,
            security_groups=[container_security_group],
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
            ),
            enable_execute_command=True,
        )

        cdk.CfnOutput(self, "ECSClusterArn", value=ecs_cluster.cluster_arn)

        self.ecs_task_role = ecs_task_role
