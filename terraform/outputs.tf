output "backup_bucket_name" {
  description = "Name of the S3 backup bucket"
  value       = aws_s3_bucket.db_backups.id
}

output "backup_bucket_arn" {
  description = "ARN of the S3 backup bucket"
  value       = aws_s3_bucket.db_backups.arn
}

output "backup_user_access_key_id" {
  description = "Access Key ID for backup user"
  value       = aws_iam_access_key.backup_user.id
  sensitive   = false
}

output "backup_user_secret_access_key" {
  description = "Secret Access Key for backup user (save this securely!)"
  value       = aws_iam_access_key.backup_user.secret
  sensitive   = true
}

output "aws_cli_configure_command" {
  description = "Command to configure AWS CLI profile for backups"
  value       = "aws configure --profile banking-backup"
}