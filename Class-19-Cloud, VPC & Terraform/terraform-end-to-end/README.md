# Session 19: End-to-End Terraform Infrastructure

## Objective

Build AWS infrastructure using Terraform to demonstrate providers,
variables, resources, outputs, dependencies, Terraform state,
planning, applying, and destroying infrastructure.

## Architecture

Terraform
   |
   +-- VPC
   |    |
   |    +-- Public Subnet
   |    +-- Internet Gateway
   |    +-- Route Table
   |    +-- Route Table Association
   |    +-- Security Group
   |    +-- EC2 Instance running Nginx
   |
   +-- S3 Bucket
        +-- Encryption
        +-- Versioning
        +-- Public Access Block

## Files

- versions.tf: Terraform and AWS provider configuration.
- variables.tf: Configurable infrastructure values.
- main.tf: AWS resources and dependencies.
- outputs.tf: Resource IDs, public IP, and bucket details.
- terraform.tfvars.example: Example input values.
- .gitignore: Excludes state and local variable files.

## Prerequisites

- Terraform >= 1.6.0
- AWS CLI
- Valid AWS credentials with permission to create and delete
  the required resources.

The AWS provider uses the configured AWS credentials and region.
Do not put AWS access keys in Terraform files or commit credentials.

## 1. Prepare Variables

Copy the example file:

    cp terraform.tfvars.example terraform.tfvars

Edit terraform.tfvars and replace the example bucket name with a
globally unique S3 bucket name.

## 2. Initialize Terraform

    terraform init

Downloads the AWS provider and prepares the working directory.

## 3. Format

    terraform fmt

Formats Terraform files consistently.

## 4. Validate

    terraform validate

Checks Terraform configuration syntax and consistency.

## 5. Plan

    terraform plan

Shows the resources Terraform intends to create, change, or destroy.
It does not create infrastructure.

Expected shape for a new deployment:

    Plan: 11 to add, 0 to change, 0 to destroy.

The exact count may differ if the configuration changes.

## 6. Apply

    terraform apply

Review the plan and enter yes only after checking the proposed changes.

This creates the VPC, subnet, Internet Gateway, route table,
route association, security group, EC2 instance, S3 bucket,
and the S3 security configuration resources.

Real AWS resources may incur charges.

## 7. Inspect State and Outputs

List the resources tracked by Terraform:

    terraform state list

View the current Terraform state:

    terraform show

Show output values:

    terraform output

Show a specific output:

    terraform output ec2_public_ip
    terraform output s3_bucket_name

Terraform state records the resources Terraform manages. Keep state
files private and do not commit them to Git.

## 8. Verify the Application

After the EC2 instance finishes starting, open the public IP shown by:

    terraform output ec2_public_ip

Use HTTP:

    http://EC2_PUBLIC_IP

The security group allows inbound HTTP on port 80. The Nginx startup
script may need a short time to finish installing and starting.

## 9. Destroy Infrastructure

When finished, inspect the deletion plan:

    terraform plan -destroy

Then remove the resources:

    terraform destroy

Review the proposed deletions and enter yes to confirm.

The S3 bucket must be empty before it can be deleted because
force_destroy is disabled. Remove any objects first if necessary.

## Important Notes

- terraform plan and terraform apply require working AWS credentials
  for this real AWS project.
- The EC2 instance and public IPv4 address can incur charges.
- Restrict SSH to a trusted IP and use an existing key pair.
- No AWS access keys should be stored in this project.