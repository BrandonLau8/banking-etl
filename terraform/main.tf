# Banking Infrastructure - S3 Backups Only
# Author: Brandon Lau
# Purpose: Automated database backups to S3

terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }

  # Optional: Store state in S3 (recommended for team/multiple machines)
  # Uncomment after creating the state bucket manually
  # backend "s3" {
  #   bucket = "banking-terraform-state"
  #   key    = "banking/terraform.tfstate"
  #   region = "us-east-1"
  #   encrypt = true
  # }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project   = "Banking"
      ManagedBy = "Terraform"
      Owner     = "BrandonLau"
    }
  }
}

# Get current AWS account ID
data "aws_caller_identity" "current" {}

# ============================================
# S3 Bucket for Database Backups
# ============================================

resource "aws_s3_bucket" "db_backups" {
  bucket = "${var.project_name}-backups-${data.aws_caller_identity.current.account_id}"

  tags = {
    Name        = "Banking DB Backups"
    Description = "PostgreSQL database backups"
  }
}

# Enable versioning (keep multiple versions of backups)
resource "aws_s3_bucket_versioning" "db_backups" {
  bucket = aws_s3_bucket.db_backups.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Enable encryption at rest
resource "aws_s3_bucket_server_side_encryption_configuration" "db_backups" {
  bucket = aws_s3_bucket.db_backups.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Block public access (security best practice)
resource "aws_s3_bucket_public_access_block" "db_backups" {
  bucket = aws_s3_bucket.db_backups.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Lifecycle policy: Delete backups older than 90 days
resource "aws_s3_bucket_lifecycle_configuration" "db_backups" {
  bucket = aws_s3_bucket.db_backups.id

  rule {
    id     = "delete-old-backups"
    status = "Enabled"

    expiration {
      days = 90
    }

    noncurrent_version_expiration {
      noncurrent_days = 30
    }
  }

  rule {
    id     = "transition-to-glacier"
    status = "Enabled"

    # Move backups older than 30 days to cheaper storage
    transition {
      days          = 30
      storage_class = "GLACIER_IR"
    }
  }
}

# ============================================
# IAM User for Backup Script (Local Access)
# ============================================

# Create IAM user for your local backup script
resource "aws_iam_user" "backup_user" {
  name = "${var.project_name}-backup-user"

  tags = {
    Description = "User for local backup script to upload to S3"
  }
}

# Create access key for the user
resource "aws_iam_access_key" "backup_user" {
  user = aws_iam_user.backup_user.name
}

# Policy allowing only S3 uploads to backup bucket
resource "aws_iam_user_policy" "backup_user" {
  name = "S3BackupUploadPolicy"
  user = aws_iam_user.backup_user.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:PutObjectAcl",
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.db_backups.arn,
          "${aws_s3_bucket.db_backups.arn}/*"
        ]
      }
    ]
  })
}

# ============================================
# Optional: SNS Topic for Backup Notifications
# ============================================

resource "aws_sns_topic" "backup_notifications" {
  count = var.enable_notifications ? 1 : 0

  name = "${var.project_name}-backup-notifications"

  tags = {
    Description = "Notifications for backup success/failure"
  }
}

resource "aws_sns_topic_subscription" "email" {
  count = var.enable_notifications ? 1 : 0

  topic_arn = aws_sns_topic.backup_notifications[0].arn
  protocol  = "email"
  endpoint  = var.notification_email
}