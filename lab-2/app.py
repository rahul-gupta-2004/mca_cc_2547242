import streamlit as st
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

st.set_page_config(page_title="S3 Manager")
st.title("Amazon S3 Manager")

# Sidebar - AWS Credentials
st.sidebar.header("AWS Credentials")
aws_access_key = st.sidebar.text_input("Access Key ID", type="password")
aws_secret_key = st.sidebar.text_input("Secret Access Key", type="password")
aws_session_token = st.sidebar.text_input("Session Token", type="password")

# Connection state
if "connected" not in st.session_state:
    st.session_state.connected = False

if st.sidebar.button("Connect to AWS"):
    if not (aws_access_key and aws_secret_key and aws_session_token):
        st.sidebar.error("Please fill in all three credential fields.")
        st.session_state.connected = False
    else:
        try:
            test_client = boto3.client(
                "s3",
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key,
                aws_session_token=aws_session_token,
            )
            test_client.list_buckets()
            st.session_state.connected = True
        except (ClientError, NoCredentialsError):
            st.session_state.connected = False
            st.sidebar.error("Connection failed. Check your credentials.")

# Show connection status
if st.session_state.connected:
    st.sidebar.success("Status: Connected")
else:
    st.sidebar.warning("Status: Not Connected")

def get_client():
    return boto3.client(
        "s3",
        aws_access_key_id=aws_access_key or None,
        aws_secret_access_key=aws_secret_key or None,
        aws_session_token=aws_session_token or None,
    )

if not st.session_state.connected:
    st.info("Connect to AWS using the sidebar to get started.")
    st.stop()

tab1, tab2, tab3 = st.tabs(["Create Bucket", "Upload Files", "Change Access"])

# Tab 1 - Create Bucket
with tab1:
    st.header("Create a New S3 Bucket")
    bucket_name = st.text_input("Bucket Name")
    region = st.selectbox("Region", [
        "us-east-1", "us-east-2", "us-west-1", "us-west-2",
        "ap-south-1", "eu-west-1", "eu-central-1"
    ])

    if st.button("Create Bucket"):
        if not bucket_name:
            st.error("Please enter a bucket name.")
        else:
            try:
                s3 = get_client()
                if region == "us-east-1":
                    s3.create_bucket(Bucket=bucket_name)
                else:
                    s3.create_bucket(
                        Bucket=bucket_name,
                        CreateBucketConfiguration={"LocationConstraint": region}
                    )
                st.success(f"Bucket '{bucket_name}' created in '{region}'!")
            except ClientError as e:
                st.error(e.response["Error"]["Message"])

# Tab 2 - Upload Files
with tab2:
    st.header("Upload Files to a Bucket")
    try:
        s3 = get_client()
        all_buckets = [b["Name"] for b in s3.list_buckets().get("Buckets", [])]
    except Exception:
        all_buckets = []

    upload_bucket = st.selectbox("Select Bucket", all_buckets or ["No buckets found"], key="upload_bucket")
    uploaded_files = st.file_uploader("Choose files", accept_multiple_files=True)

    if st.button("Upload Files"):
        if not uploaded_files:
            st.error("Please select at least one file.")
        else:
            s3 = get_client()
            for file in uploaded_files:
                try:
                    s3.upload_fileobj(file, upload_bucket, file.name)
                    st.success(f"Uploaded '{file.name}' to '{upload_bucket}'")
                except ClientError as e:
                    st.error(f"{file.name}: {e.response['Error']['Message']}")

# Tab 3 - Change Access
with tab3:
    st.header("Change Object Access Level")
    try:
        s3 = get_client()
        all_buckets = [b["Name"] for b in s3.list_buckets().get("Buckets", [])]
    except Exception:
        all_buckets = []

    acl_bucket = st.selectbox("Select Bucket", all_buckets or ["No buckets found"], key="acl_bucket")

    objects = []
    if acl_bucket and acl_bucket != "No buckets found":
        try:
            s3 = get_client()
            resp = s3.list_objects_v2(Bucket=acl_bucket)
            objects = [o["Key"] for o in resp.get("Contents", [])]
        except Exception:
            objects = []

    selected_object = st.selectbox("Select File", objects or ["No files found"])

    acl_choice = st.selectbox("Access Level", [
        "private", "public-read", "public-read-write", "authenticated-read"
    ])

    if st.button("Apply Access Level"):
        if not objects:
            st.error("No file selected.")
        else:
            try:
                s3 = get_client()
                s3.put_object_acl(Bucket=acl_bucket, Key=selected_object, ACL=acl_choice)
                st.success(f"Access for '{selected_object}' changed to '{acl_choice}'.")

                acl_resp = s3.get_object_acl(Bucket=acl_bucket, Key=selected_object)
                st.subheader("Current Grants")
                for grant in acl_resp.get("Grants", []):
                    grantee = grant["Grantee"]
                    name = grantee.get("DisplayName") or grantee.get("URI", "Unknown")
                    st.write(f"{name} => {grant['Permission']}")

            except ClientError as e:
                err_code = e.response["Error"]["Code"]
                if err_code == "AccessControlListNotSupported":
                    st.warning("This bucket has Block Public Access or Object Ownership settings that prevent ACL changes. Disable them in the AWS Console first.")
                else:
                    st.error(e.response["Error"]["Message"])