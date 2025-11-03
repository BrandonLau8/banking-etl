variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name (used for resource naming)"
  type        = string
  default     = "banking"
}

variable "enable_notifications" {
  description = "Enable SNS notifications for backups"
  type        = bool
  default     = false
}

variable "notification_email" {
  description = "Email address for backup notifications"
  type        = string
  default     = ""
}