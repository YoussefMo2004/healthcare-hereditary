output "repository_url" {
  description = "Full ECR repository URL (account.dkr.ecr.region.amazonaws.com/name)."
  value       = aws_ecr_repository.api.repository_url
}

output "registry_url" {
  description = "ECR registry URL (without repository name) — used for docker login."
  value       = "${data.aws_caller_identity.current.account_id}.dkr.ecr.${data.aws_region.current.name}.amazonaws.com"
}

output "repository_arn" {
  description = "ARN of the ECR repository."
  value       = aws_ecr_repository.api.arn
}
