import os
import boto3

AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID", "YOUR_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get(
    "AWS_SECRET_ACCESS_KEY", "YOUR_SECRET_ACCESS_KEY"
)
AWS_SESSION_TOKEN = os.environ.get("AWS_SESSION_TOKEN", "YOUR_SESSION_TOKEN")

REGION_NAME = "us-east-1"

BUCKET_NAME = "2547242"  # Using your actual bucket name from your console
REPORT_FILE_NAME = "aws_resource_report.txt"

# Initialize S3 and EC2 clients using explicit session credentials
session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    aws_session_token=AWS_SESSION_TOKEN,
    region_name=REGION_NAME,
)

s3_client = session.client("s3")
ec2_resource = session.resource("ec2")


def generate_aws_report():
    report_content = []
    report_content.append("==================================================")
    report_content.append("           AWS RESOURCE INVENTORY REPORT          ")
    report_content.append("==================================================\n")

    # --- PART 1: Fetch and Compile EC2 Instance Details ---
    report_content.append("--- EC2 INSTANCE DETAILS ---")
    try:
        instances = ec2_resource.instances.filter(
            Filters=[{"Name": "instance-state-name", "Values": ["running"]}]
        )
        instance_count = 0
        for instance in instances:
            instance_count += 1
            name = "N/A"
            if instance.tags:
                for tag in instance.tags:
                    if tag["Key"] == "Name":
                        name = tag["Value"]
                        break
            ip = (
                instance.public_ip_address
                if instance.public_ip_address
                else "No Public IP"
            )
            report_content.append(f"Instance #{instance_count}:")
            report_content.append(f"  - Instance ID:        {instance.id}")
            report_content.append(f"  - Instance Name:      {name}")
            report_content.append(f"  - Instance Type:      {instance.instance_type}")
            report_content.append(f"  - State:              {instance.state['Name']}")
            report_content.append(f"  - Public IPv4 Address: {ip}\n")

        if instance_count == 0:
            report_content.append("No running EC2 instances found.\n")
    except Exception as e:
        report_content.append(f"Error fetching EC2 data: {str(e)}\n")

    # --- PART 2: Fetch S3 Bucket Objects & Structure ---
    report_content.append("--- S3 BUCKET INVENTORY DETAILS ---")
    report_content.append(f"Bucket Name: {BUCKET_NAME}\n")
    report_content.append(
        f"{'Folder Name':<15} | {'Object Name':<25} | {'Size (Bytes)':<12}"
    )
    report_content.append("-" * 60)

    try:
        response = s3_client.list_objects_v2(Bucket=BUCKET_NAME)

        # Print layout to console simultaneously for verification
        print("Displaying current S3 objects structure:")

        if "Contents" in response:
            for obj in response["Contents"]:
                key = obj["Key"]
                size = obj["Size"]

                # Deduce folder and filename details from key path
                if "/" in key:
                    folder_name, object_name = key.split("/", 1)
                else:
                    folder_name = "root"
                    object_name = key

                # Skip empty directory placeholders if present
                if not object_name:
                    continue

                # Add row to inventory data string
                row_string = f"{folder_name:<15} | {object_name:<25} | {size:<12}"
                report_content.append(row_string)
                print(f" - Found: {key} ({size} bytes)")
        else:
            report_content.append("No objects found inside the bucket structure.")
            print("Bucket is currently empty.")

    except Exception as e:
        report_content.append(f"Error fetching S3 objects: {str(e)}")
        print(f"Error checking S3: {e}")

    report_content_string = "\n".join(report_content)

    # --- PART 3: Save Report Locally (d) ---
    with open(REPORT_FILE_NAME, "w") as file:
        file.write(report_content_string)
    print(f"\n[✓] Locally saved full report to: {REPORT_FILE_NAME}")

    # --- PART 4: Upload Report to S3 & Verify (e) ---
    try:
        print(f"Uploading report to S3 bucket '{BUCKET_NAME}'...")
        s3_client.upload_file(REPORT_FILE_NAME, BUCKET_NAME, REPORT_FILE_NAME)

        # Verification step: check metadata to confirm successful execution
        print("Verifying upload status...")
        verify_response = s3_client.head_object(
            Bucket=BUCKET_NAME, Key=REPORT_FILE_NAME
        )
        if verify_response:
            print("\n" + "=" * 55)
            print("SUCCESS: Inventory report generated, saved, and verified!")
            print(f"S3 Object Path: s3://{BUCKET_NAME}/{REPORT_FILE_NAME}")
            print("=" * 55)

    except Exception as e:
        print(f"\n[✗] Upload/Verification failed: {str(e)}")


if __name__ == "__main__":
    generate_aws_report()