# Select an available Availability Zone.
data "aws_availability_zones" "available" {
  state = "available"
}

# Find the latest Amazon Linux 2023 x86_64 AMI.
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-2023.*-x86_64"]
  }

  filter {
    name   = "architecture"
    values = ["x86_64"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  filter {
    name   = "root-device-type"
    values = ["ebs"]
  }
}

# 1. Create the VPC.
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name      = "${var.project_name}-vpc"
    ManagedBy = "Terraform"
  }
}

# 2. Create a public subnet.
resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.public_subnet_cidr
  availability_zone       = data.aws_availability_zones.available.names[0]
  map_public_ip_on_launch = true

  tags = {
    Name      = "${var.project_name}-public-subnet"
    ManagedBy = "Terraform"
  }
}

# 3. Create an Internet Gateway.
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name      = "${var.project_name}-igw"
    ManagedBy = "Terraform"
  }
}

# 4. Create a public route table.
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name      = "${var.project_name}-public-rt"
    ManagedBy = "Terraform"
  }
}

# 5. Associate the route table with the subnet.
resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

# 6. Create a security group for the web server.
resource "aws_security_group" "web" {
  name        = "${var.project_name}-web-sg"
  description = "Allow HTTP and optional restricted SSH"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # SSH is enabled only when both a key pair and trusted IP are provided.
  dynamic "ingress" {
    for_each = (
      var.key_name != null && var.ssh_allowed_cidr != null
      ? [var.ssh_allowed_cidr]
      : []
    )

    content {
      description = "SSH from trusted IP"
      from_port   = 22
      to_port     = 22
      protocol    = "tcp"
      cidr_blocks = [ingress.value]
    }
  }

  egress {
    description = "Allow outbound IPv4"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name      = "${var.project_name}-web-sg"
    ManagedBy = "Terraform"
  }
}

# 7. Create an EC2 instance running Nginx.
resource "aws_instance" "web" {
  ami                         = data.aws_ami.amazon_linux.id
  instance_type               = var.instance_type
  subnet_id                   = aws_subnet.public.id
  vpc_security_group_ids      = [aws_security_group.web.id]
  associate_public_ip_address = true
  key_name                    = var.key_name

  user_data = <<-EOF
    #!/bin/bash
    dnf install -y nginx
    systemctl enable --now nginx
    cat > /usr/share/nginx/html/index.html <<'HTML'
    <h1>Session 19 Terraform Infrastructure</h1>
    <p>Nginx is running on an EC2 instance.</p>
    HTML
  EOF

  user_data_replace_on_change = true

  # Ensure the public subnet routing is configured first.
  depends_on = [
    aws_route_table_association.public
  ]

  tags = {
    Name      = "${var.project_name}-ec2"
    ManagedBy = "Terraform"
  }
}

# 8. Create the S3 bucket.
resource "aws_s3_bucket" "demo" {
  bucket = var.bucket_name

  # Keep force_destroy disabled to protect bucket contents.
  force_destroy = false

  tags = {
    Name        = "${var.project_name}-bucket"
    Environment = "practice"
    ManagedBy   = "Terraform"
  }
}

# Block all public access to the bucket.
resource "aws_s3_bucket_public_access_block" "demo" {
  bucket = aws_s3_bucket.demo.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Enable S3 versioning.
resource "aws_s3_bucket_versioning" "demo" {
  bucket = aws_s3_bucket.demo.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Enable server-side encryption using S3-managed keys.
resource "aws_s3_bucket_server_side_encryption_configuration" "demo" {
  bucket = aws_s3_bucket.demo.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}