
# AWS Cloud Infrastructure - CIA 1

## Overview

This project demonstrates the creation and configuration of secure storage, access management, and compute infrastructure within AWS Academy Learner Lab.

## Key Configurations

1. **S3 Storage:** Created bucket `2547242` with `ufolder/userfile.xlsx` and `efolder/employeefile.xlsx`.
2. **Access Control:** Implemented bucket policy allowing web app access to `ufolder` while explicitly denying access to `efolder`.
3. **Data Management:** Enabled Bucket Versioning and configured a 30-day Lifecycle transition rule to Standard-IA.
4. **EC2 Web Server:** Launched an Ubuntu instance hosting a custom page displaying Student Name (Rahul Gupta) and Register Number.
5. **Security Groups:** Configured Inbound rules to open Ports 22 (SSH) and 80 (HTTP) for public web access.
6. **Automation via Boto3:** Included Python scripts to manage S3 objects, list instances, and auto-upload an inventory report.

**Student:** Rahul Gupta | **Register Number:** 2547242