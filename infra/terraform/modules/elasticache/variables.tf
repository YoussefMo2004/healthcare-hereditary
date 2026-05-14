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
  description = "Security group IDs allowed to reach Redis."
  type        = list(string)
}

variable "node_type" {
  type = string
}

variable "engine_version" {
  type = string
}

variable "num_cache_nodes" {
  type = number
}
