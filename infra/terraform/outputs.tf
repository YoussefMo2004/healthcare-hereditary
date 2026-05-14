# ── Cluster ────────────────────────────────────────────────────────────────────

output "cluster_name" {
  description = "EKS cluster name."
  value       = module.eks.cluster_name
}

output "cluster_endpoint" {
  description = "EKS API server endpoint."
  value       = module.eks.cluster_endpoint
}

output "kubeconfig_command" {
  description = "Run this command to update your local kubeconfig."
  value       = "aws eks update-kubeconfig --region ${var.aws_region} --name ${module.eks.cluster_name}"
}

# ── ECR ────────────────────────────────────────────────────────────────────────

output "ecr_repository_url" {
  description = "ECR repository URL for the healthcare-api image."
  value       = module.ecr.repository_url
}

output "docker_login_command" {
  description = "Authenticate Docker with ECR."
  value       = "aws ecr get-login-password --region ${var.aws_region} | docker login --username AWS --password-stdin ${module.ecr.registry_url}"
}

# ── Database ───────────────────────────────────────────────────────────────────

output "rds_endpoint" {
  description = "RDS PostgreSQL endpoint (host:port)."
  value       = module.rds.endpoint
  sensitive   = true
}

output "redis_endpoint" {
  description = "ElastiCache Redis primary endpoint."
  value       = module.elasticache.endpoint
  sensitive   = true
}

# ── Networking ─────────────────────────────────────────────────────────────────

output "vpc_id" {
  description = "VPC ID."
  value       = module.vpc.vpc_id
}

output "private_subnet_ids" {
  description = "Private subnet IDs used by EKS nodes and databases."
  value       = module.vpc.private_subnet_ids
}
