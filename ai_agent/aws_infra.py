import os
import boto3


class AWSInfrastructure:
    """Simplified helper for provisioning AWS resources for the agent."""

    def __init__(self, region: str | None = None):
        self.region = region or os.environ.get("AWS_REGION", "us-east-1")
        self.ec2 = boto3.resource("ec2", region_name=self.region)

    def launch_ec2_instance(
        self,
        ami_id: str,
        instance_type: str = "t3.micro",
        key_name: str | None = None,
        security_group_ids: list[str] | None = None,
    ) -> str:
        """Launch a single EC2 instance and return its ID."""
        params = {
            "ImageId": ami_id,
            "InstanceType": instance_type,
            "MinCount": 1,
            "MaxCount": 1,
        }
        if key_name:
            params["KeyName"] = key_name
        if security_group_ids:
            params["SecurityGroupIds"] = security_group_ids

        instances = self.ec2.create_instances(**params)
        instance = instances[0]
        print(f"Launched EC2 instance {instance.id}")
        return instance.id

