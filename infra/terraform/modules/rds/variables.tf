variable "name_prefix" {
  type = string
}

variable "vpc_id" {
  type = string
}

variable "private_subnet_ids" {
  type = list(string)
}

variable "allowed_security_groups" {
  description = "Security group IDs allowed to reach the RDS instance (e.g., EKS nodes)."
  type        = list(string)
}

variable "instance_class" {
  type = string
}

variable "allocated_storage_gb" {
  type = number
}

variable "max_allocated_storage_gb" {
  type = number
}

variable "postgres_version" {
  type = string
}

variable "database_name" {
  type = string
}

variable "username" {
  type = string
}

variable "multi_az" {
  type = bool
}

variable "deletion_protection" {
  type = bool
}
