"""Script to add SSH configuration for SSM tunnel initiation."""

import os

import aws_cdk.cx_api as cx_api
import boto3
from sshconf import read_ssh_config

cloud_assembly = cx_api.CloudAssembly("cdk.out")
stack_name = cloud_assembly.stacks[0].stack_name
region = os.environ["AWS_REGION"]

statuses = ["ROLLBACK_COMPLETE", "CREATE_COMPLETE", "UPDATE_COMPLETE"]
cloudformation = boto3.resource("cloudformation", region_name=region)
ecs_client = boto3.client("ecs", region_name=region)
stacks = [
    stack
    for stack in cloudformation.stacks.filter(StackName=stack_name)
    if stack.stack_status in statuses
]
if len(stacks) == 1:
    template = cloud_assembly.stacks[0].template
    resources = template["Resources"].items()
    for resource_logical_id, resource_detail in resources:
        if resource_detail["Type"] == "AWS::ECS::Cluster":
            cluster_logical_id = resource_logical_id

cluster_list = ecs_client.list_clusters()
for cluster_arn in cluster_list["clusterArns"]:
    if cluster_logical_id in cluster_arn:
        ecs_cluster_arn = cluster_arn

tasks_list = ecs_client.list_tasks(cluster=ecs_cluster_arn)
for task_arn in tasks_list["taskArns"]:
    if cluster_logical_id in task_arn:
        ecs_task_arn = task_arn

containers_list = ecs_client.describe_tasks(
    cluster=ecs_cluster_arn, tasks=[ecs_task_arn]
)["tasks"][0]["containers"]

cluster_name = ecs_task_arn.split(":")[5].split("/")[1]
task_id = ecs_task_arn.split(":")[5].split("/")[2]
container_runtime_id = containers_list[0]["runtimeId"]

ssm_target = f"ecs:{cluster_name}_{task_id}_{container_runtime_id}"

cf_client = boto3.client("cloudformation", region_name=region)
response = cf_client.describe_stacks(StackName=stack_name)
outputs = response["Stacks"][0]["Outputs"]
for output in outputs:
    keyName = output["OutputKey"]
    if "DBConstructAuroraClusterEndpoint" in keyName:
        rds_host = output["OutputValue"]

print("Setting up proxy...")

proxy_command = f'sh -c "aws ssm start-session --region {region} --target %n --document-name AWS-StartPortForwardingSessionToRemoteHost --parameters portNumber=3306,localPortNumber=9999,host={rds_host}"'  # noqa: E501

filename = os.path.expanduser("~/.ssh/config")
if not os.path.exists(filename):
    with open(filename, "w"):
        pass
    print("File ~/.ssh/config didn't exist. Creating the file...")

c = read_ssh_config(filename)

try:
    c.remove('"ssm-db-proxy"')
except Exception:
    pass
finally:
    c.add('"ssm-db-proxy"', Hostname=ssm_target, ProxyCommand=proxy_command)
    c.save()

print(
    f"Run the following command to activate the tunnel proxy:\r\nssh ssm-db-proxy\r\nand then on another shell, run\r\n./scripts/mysql_connect.sh -r {region} -s {stack_name}\r\nto connect to the database with temporary credentials"  # noqa: E501
)
