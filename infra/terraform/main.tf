provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = var.project
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}

# Kubernetes and Helm providers are configured after EKS is created.
provider "kubernetes" {
  host                   = module.eks.cluster_endpoint
  cluster_ca_certificate = base64decode(module.eks.cluster_ca_certificate)
  token                  = data.aws_eks_cluster_auth.cluster.token
}

provider "helm" {
  kubernetes {
    host                   = module.eks.cluster_endpoint
    cluster_ca_certificate = base64decode(module.eks.cluster_ca_certificate)
    token                  = data.aws_eks_cluster_auth.cluster.token
  }
}

data "aws_eks_cluster_auth" "cluster" {
  name = module.eks.cluster_name
}

# ── Locals ─────────────────────────────────────────────────────────────────────

locals {
  name_prefix = "${var.project}-${var.environment}"
}

# ── VPC ────────────────────────────────────────────────────────────────────────

module "vpc" {
  source = "./modules/vpc"

  name_prefix        = local.name_prefix
  vpc_cidr           = var.vpc_cidr
  availability_zones = var.availability_zones
}

# ── EKS ────────────────────────────────────────────────────────────────────────

module "eks" {
  source = "./modules/eks"

  name_prefix         = local.name_prefix
  kubernetes_version  = var.kubernetes_version
  vpc_id              = module.vpc.vpc_id
  private_subnet_ids  = module.vpc.private_subnet_ids
  node_instance_types = var.node_instance_types
  node_min_size       = var.node_min_size
  node_max_size       = var.node_max_size
  node_desired_size   = var.node_desired_size
}

# ── RDS PostgreSQL ─────────────────────────────────────────────────────────────

module "rds" {
  source = "./modules/rds"

  name_prefix              = local.name_prefix
  vpc_id                   = module.vpc.vpc_id
  private_subnet_ids       = module.vpc.private_subnet_ids
  allowed_security_groups  = [module.eks.node_security_group_id]
  instance_class           = var.rds_instance_class
  allocated_storage_gb     = var.rds_allocated_storage_gb
  max_allocated_storage_gb = var.rds_max_allocated_storage_gb
  postgres_version         = var.rds_postgres_version
  database_name            = var.rds_database_name
  username                 = var.rds_username
  multi_az                 = var.rds_multi_az
  deletion_protection      = var.rds_deletion_protection
}

# ── ElastiCache Redis ──────────────────────────────────────────────────────────

module "elasticache" {
  source = "./modules/elasticache"

  name_prefix             = local.name_prefix
  vpc_id                  = module.vpc.vpc_id
  private_subnet_ids      = module.vpc.private_subnet_ids
  allowed_security_groups = [module.eks.node_security_group_id]
  node_type               = var.redis_node_type
  engine_version          = var.redis_engine_version
  num_cache_nodes         = var.redis_num_cache_nodes
}

# ── ECR ────────────────────────────────────────────────────────────────────────

module "ecr" {
  source = "./modules/ecr"

  name_prefix           = local.name_prefix
  image_tag_mutability  = var.ecr_image_tag_mutability
  image_retention_count = var.ecr_image_retention_count
}

# ── Kubernetes: core cluster resources ────────────────────────────────────────

resource "kubernetes_namespace" "healthcare" {
  metadata {
    name = "healthcare"
    labels = {
      "app.kubernetes.io/managed-by" = "terraform"
      environment                    = var.environment
    }
  }

  depends_on = [module.eks]
}

# Store RDS credentials as a Kubernetes Secret so pods can consume them.
resource "kubernetes_secret" "rds_credentials" {
  metadata {
    name      = "rds-credentials"
    namespace = kubernetes_namespace.healthcare.metadata[0].name
  }

  data = {
    host     = module.rds.endpoint
    port     = "5432"
    database = var.rds_database_name
    username = var.rds_username
    password = module.rds.password
    dsn      = "postgresql://${var.rds_username}:${module.rds.password}@${module.rds.endpoint}:5432/${var.rds_database_name}"
  }

  type = "Opaque"
}

resource "kubernetes_secret" "redis_credentials" {
  metadata {
    name      = "redis-credentials"
    namespace = kubernetes_namespace.healthcare.metadata[0].name
  }

  data = {
    host     = module.elasticache.endpoint
    port     = "6379"
    password = module.elasticache.auth_token
    url      = "redis://:${module.elasticache.auth_token}@${module.elasticache.endpoint}:6379/0"
  }

  type = "Opaque"
}

# ── Helm: AWS Load Balancer Controller ────────────────────────────────────────

resource "helm_release" "aws_load_balancer_controller" {
  name       = "aws-load-balancer-controller"
  repository = "https://aws.github.io/eks-charts"
  chart      = "aws-load-balancer-controller"
  namespace  = "kube-system"
  version    = "1.7.2"

  set {
    name  = "clusterName"
    value = module.eks.cluster_name
  }

  set {
    name  = "serviceAccount.annotations.eks\\.amazonaws\\.com/role-arn"
    value = module.eks.load_balancer_controller_role_arn
  }

  depends_on = [module.eks]
}

# ── Helm: metrics-server (needed for HPA) ─────────────────────────────────────

resource "helm_release" "metrics_server" {
  name       = "metrics-server"
  repository = "https://kubernetes-sigs.github.io/metrics-server/"
  chart      = "metrics-server"
  namespace  = "kube-system"
  version    = "3.12.1"

  depends_on = [module.eks]
}
