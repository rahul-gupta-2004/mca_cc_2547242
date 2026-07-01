import boto3
import os

AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID", "YOUR_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get(
    "AWS_SECRET_ACCESS_KEY", "YOUR_SECRET_ACCESS_KEY"
)
AWS_SESSION_TOKEN = os.environ.get("AWS_SESSION_TOKEN", "YOUR_SESSION_TOKEN")

REGION_NAME = "us-east-1"  # Default region for Learner Lab

# Initialize the EC2 resource with your session credentials
ec2_resource = boto3.resource(
    "ec2",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    aws_session_token=AWS_SESSION_TOKEN,
    region_name=REGION_NAME,
)


def get_running_instances():
    print("Fetching running EC2 instances...\n")

    # Filter instances to only look for those in the 'running' state
    running_instances = ec2_resource.instances.filter(
        Filters=[{"Name": "instance-state-name", "Values": ["running"]}]
    )

    instance_count = 0

    for instance in running_instances:
        instance_count += 1

        # Extract the Instance Name from its Tags list
        instance_name = "N/A"
        if instance.tags:
            for tag in instance.tags:
                if tag["Key"] == "Name":
                    instance_name = tag["Value"]
                    break

        # Extract required attributes
        instance_id = instance.id
        instance_type = instance.instance_type
        instance_state = instance.state["Name"]
        public_ip = (
            instance.public_ip_address
            if instance.public_ip_address
            else "No Public IP"
        )

        # Print the formatted details
        print(f"Instance #{instance_count}")
        print(f"  - Name:               {instance_name}")
        print(f"  - Instance ID:        {instance_id}")
        print(f"  - Instance Type:      {instance_type}")
        print(f"  - Instance State:     {instance_state}")
        print(f"  - Public IPv4 Address: {public_ip}")
        print("-" * 40)

    if instance_count == 0:
        print("No running EC2 instances found in this account.")


if __name__ == "__main__":
    get_running_instances()