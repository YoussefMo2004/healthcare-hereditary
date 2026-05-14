output "endpoint" {
  description = "Primary endpoint hostname for the Redis cluster."
  value       = aws_elasticache_cluster.this.cache_nodes[0].address
  sensitive   = true
}

output "port" {
  description = "Redis port."
  value       = aws_elasticache_cluster.this.cache_nodes[0].port
}

output "auth_token" {
  description = "AUTH token for Redis connections."
  value       = random_password.redis.result
  sensitive   = true
}

output "security_group_id" {
  description = "Security group ID for the Redis cluster."
  value       = aws_security_group.redis.id
}
