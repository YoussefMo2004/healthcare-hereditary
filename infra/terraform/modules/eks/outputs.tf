output "cluster_name" {
  description = "EKS cluster name."
  value       = aws_eks_cluster.this.name
}

output "cluster_endpoint" {
  description = "EKS API server endpoint."
  value       = aws_eks_cluster.this.endpoint
}

output "cluster_ca_certificate" {
  description = "Base64-encoded cluster CA certificate."
  value       = aws_eks_cluster.this.certificate_authority[0].data
}

output "node_security_group_id" {
  description = "Security group ID attached to EKS worker nodes."
  value       = aws_security_group.node.id
}

output "oidc_provider_arn" {
  description = "ARN of the OIDC identity provider (for IRSA)."
  value       = aws_iam_openid_connect_provider.cluster.arn
}

output "oidc_provider_url" {
  description = "URL of the OIDC identity provider."
  value       = aws_iam_openid_connect_provider.cluster.url
}

output "load_balancer_controller_role_arn" {
  description = "IAM role ARN for the AWS Load Balancer Controller."
  value       = aws_iam_role.load_balancer_controller.arn
}
