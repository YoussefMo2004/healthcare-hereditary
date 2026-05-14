# ── Global ─────────────────────────────────────────────────────────────────────

variable "aws_region" {
  description = "AWS region for all resources."
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Deployment environment (staging | production)."
  type        = string
  default     = "staging"
  validation {
    condition     = contains(["staging", "production"], var.environment)
    error_message = "environment must be 'staging' or 'production'."
  }
}

variable "project" {
  description = "Short project name — used as a prefix for all resource names."
  type        = string
  default     = "healthcare"
}

# ── Networking ─────────────────────────────────────────────────────────────────

variable "vpc_cidr" {
  description = "CIDR block for the VPC."
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "List of AZs to use (must be ≥ 2 for EKS + RDS)."
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b", "us-east-1c"]
}

# ── EKS ────────────────────────────────────────────────────────────────────────

variable "kubernetes_version" {
  description = "Kubernetes version for the EKS cluster."
  type        = string
  default     = "1.29"
}

variable "node_instance_types" {
  description = "EC2 instance types for the EKS managed node group."
  type        = list(string)
  default     = ["t3.large"]
}

variable "node_min_size" {
  description = "Minimum number of EKS worker nodes."
  type        = number
  default     = 2
}

variable "node_max_size" {
  description = "Maximum number of EKS worker nodes."
  type        = number
  default     = 6
}

variable "node_desired_size" {
  description = "Desired number of EKS worker nodes."
  type        = number
  default     = 3
}

# ── RDS PostgreSQL ─────────────────────────────────────────────────────────────

variable "rds_instance_class" {
  description = "RDS instance type for PostgreSQL."
  type        = string
  default     = "db.t3.medium"
}

variable "rds_allocated_storage_gb" {
  description = "Initial allocated storage for RDS in GiB."
  type        = number
  default     = 50
}

variable "rds_max_allocated_storage_gb" {
  description = "Maximum storage for RDS autoscaling in GiB."
  type        = number
  default     = 200
}

variable "rds_postgres_version" {
  description = "PostgreSQL engine version."
  type        = string
  default     = "15.6"
}

variable "rds_database_name" {
  description = "Name of the initial database."
  type        = string
  default     = "healthcare"
}

variable "rds_username" {
  description = "Master username for the RDS instance."
  type        = string
  default     = "healthcare_app"
}

variable "rds_multi_az" {
  description = "Enable Multi-AZ deployment for RDS (recommended for production)."
  type        = bool
  default     = false
}

variable "rds_deletion_protection" {
  description = "Enable RDS deletion protection."
  type        = bool
  default     = true
}

# ── ElastiCache Redis ──────────────────────────────────────────────────────────

variable "redis_node_type" {
  description = "ElastiCache node type."
  type        = string
  default     = "cache.t3.small"
}

variable "redis_engine_version" {
  description = "Redis engine version."
  type        = string
  default     = "7.1"
}

variable "redis_num_cache_nodes" {
  description = "Number of cache nodes (1 = single-node, >1 = cluster)."
  type        = number
  default     = 1
}

# ── ECR ────────────────────────────────────────────────────────────────────────

variable "ecr_image_tag_mutability" {
  description = "Image tag mutability: MUTABLE or IMMUTABLE."
  type        = string
  default     = "IMMUTABLE"
}

variable "ecr_image_retention_count" {
  description = "Number of tagged images to keep in ECR before pruning older ones."
  type        = number
  default     = 30
}
