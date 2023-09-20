from aws_cdk import CfnOutput
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_iam as iam
from aws_cdk.aws_ec2 import IMachineImage
from constructs import Construct


class EC2Construct(Construct):

    def __init__(self, scope: Construct, id_: str, vpc: ec2.IVpc,  instance_security_group: ec2.SecurityGroup) -> None:
        super().__init__(scope, id_)
        
        amzn_linux: IMachineImage = ec2.MachineImage.latest_amazon_linux(
            generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
            edition=ec2.AmazonLinuxEdition.STANDARD,
            virtualization=ec2.AmazonLinuxVirt.HVM,
            storage=ec2.AmazonLinuxStorage.GENERAL_PURPOSE,
        )

        # Instance Role and SSM Managed Policy
        role = iam.Role(
            self,
            'EC2RoleForZeroTrustDemo',
            assumed_by=iam.ServicePrincipal('ec2.amazonaws.com'),
        )

        role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name('AmazonSSMManagedInstanceCore'))
    
        # Instance
        self.instance = ec2.Instance(self,
            'DemoPrivateSubnetInstance',
            instance_type=ec2.InstanceType('t3.nano'),
            machine_image=amzn_linux,
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED),  
            security_group=instance_security_group,
            role=role,
            #replace the key_name with comment to enter custom key or get as a parameter
            key_name='EyalKeyPairIreland'
        )
