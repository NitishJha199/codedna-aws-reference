locals {
  services = {
    order-api = {
      container_port = 8000
    }

    inventory-service = {
      container_port = 8001
    }
  }

  availability_zones = [
    "${var.aws_region}a",
    "${var.aws_region}b",
  ]
}
