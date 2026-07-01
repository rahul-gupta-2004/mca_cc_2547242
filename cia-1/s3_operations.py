import os
import boto3

AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID", "YOUR_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get(
    "AWS_SECRET_ACCESS_KEY", "YOUR_SECRET_ACCESS_KEY"
)
AWS_SESSION_TOKEN = os.environ.get("AWS_SESSION_TOKEN", "YOUR_SESSION_TOKEN")

BUCKET_NAME = "2547242"
LOCAL_FILE = "userfile_2.xlsx"
S3_KEY = "ufolder/userfile_2.xlsx"

# Initialize S3 client with session tokens
s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    aws_session_token=AWS_SESSION_TOKEN,
)


def run_s3_tasks():
    # 1. Upload file
    if os.path.exists(LOCAL_FILE):
        print(f"Uploading {LOCAL_FILE} to s3://{BUCKET_NAME}/{S3_KEY}...")
        s3_client.upload_file(LOCAL_FILE, BUCKET_NAME, S3_KEY)
        print("Upload successful.")
    else:
        print(f"Error: Local file '{LOCAL_FILE}' not found. Please create it first.")
        return

    # 2. List objects
    print(f"\nListing objects in bucket '{BUCKET_NAME}':")
    response = s3_client.list_objects_v2(Bucket=BUCKET_NAME)

    if "Contents" in response:
        for obj in response["Contents"]:
            print(f" - {obj['Key']} (Size: {obj['Size']} bytes)")
    else:
        print("Bucket is empty.")

    # 3. Print success message
    print("\n" + "=" * 40)
    print("SUCCESS: All S3 operations completed successfully!")
    print("=" * 40)


if __name__ == "__main__":
    run_s3_tasks()