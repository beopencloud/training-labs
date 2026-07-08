# Module 07 — Terraform main.tf (à compléter)
# Formation DevOps Avancé · BeOpen IT

terraform {
  required_version = ">= 1.6"
  required_providers {
    local = { source = "hashicorp/local"; version = "~> 2.4" }
  }
}

# TODO FR : Définir les environnements dans un objet locals
# TODO EN : Define environments in a locals block
locals {
  environments = {
    # staging = { replicas = 2, app_version = "1.0.0", ... }
    # production = { ... }
  }
}

# TODO FR : Appeler le module app-server pour chaque environnement avec for_each
# TODO EN : Call the app-server module for each environment using for_each
