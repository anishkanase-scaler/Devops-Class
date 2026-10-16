variable "aws_region" {
  description = "AWS region for the infrastructure."
  type        = string
  default     = "ap-south-1"
}

variable "project_name" {
  description = "Prefix used for resource names and tags."
  type        = string
  default     = "session19-demo"
}

variable "vpc_cidr" {
  description = "CIDR range for the VPC."
  type        = string
  default     = "10.20.0.0/16"
}

variable "public_subnet_cidr" {
  description = "CIDR range for the public subnet."
  type        = string
  default     = "10.20.1.0/24"
}

variable "instance_type" {
  description = "EC2 instance type."
  type        = string
  default     = "t3.micro"
}

variable "bucket_name" {
  description = "Globally unique name for the S3 bucket."
  type        = string

  validation {
    condition = (
      length(var.bucket_name) >= 3 &&
      length(var.bucket_name) <= 63 &&
      can(regex("^[a-z0-9][a-z0-9.-]*[a-z0-9]$", var.bucket_name)) &&
      !strcontains(var.bucket_name, "..")
    )
    error_message = "Use a 3-63 character S3 bucket name with lowercase letters, numbers, periods, or hyphens."
  }
}

variable "key_name" {
  description = "Existing EC2 key pair name; null disables SSH access."
  type        = string
  default     = null
}

variable "ssh_allowed_cidr" {
  description = "Your trusted public IP in CIDR format, such as 203.0.113.10/32."
  type        = string
  default     = null
}