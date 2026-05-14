output "endpoint" {
  description = "RDS instance hostname (without port)."
  value       = aws_db_instance.this.address
  sensitive   = true
}

output "port" {
  description = "RDS instance port."
  value       = aws_db_instance.this.port
}

output "password" {
  description = "Generated master password."
  value       = random_password.db.result
  sensitive   = true
}

output "security_group_id" {
  description = "Security group ID for the RDS instance."
  value       = aws_security_group.rds.id
}
