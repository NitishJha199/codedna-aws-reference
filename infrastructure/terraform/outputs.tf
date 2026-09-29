output "vpc_id" {
  value = aws_vpc.main.id
}

output "ecr_repository_urls" {
  value = {
    for name, repository in aws_ecr_repository.service :
    name => repository.repository_url
  }
}

output "alb_dns_name" {
  value = aws_lb.main.dns_name
}

output "ecs_cluster_name" {
  value = aws_ecs_cluster.main.name
}

output "github_deploy_role_arn" {
  value = aws_iam_role.github_deploy.arn
}

output "database_endpoint" {
  value = aws_db_instance.main.address
}

output "database_secret_arn" {
  value     = aws_secretsmanager_secret.database.arn
  sensitive = true
}
