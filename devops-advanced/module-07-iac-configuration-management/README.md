# Module 07 — Infrastructure as Code et Configuration Management

> 🇫🇷 [Français](#français) | 🇬🇧 [English](#english)

---

## Français

### 🎯 Objectifs

- Provisionner une infrastructure locale avec Terraform (modules, state, workspace)
- Appliquer une configuration système avec Ansible (playbooks, rôles, inventaires)
- Comprendre la différence entre provisioning (Terraform) et configuration (Ansible)
- Combiner les deux dans un workflow complet

---

### 🔧 Prérequis

| Outil | Vérification |
|-------|--------------|
| Terraform 1.6+ | `terraform --version` |
| Ansible 2.15+ | `ansible --version` |
| Docker | Pour les conteneurs cibles Ansible |

---

### ⏱️ Durée estimée

**2h**

---

### 📁 Fichiers fournis

```
module-07-iac-configuration-management/
├── README.md
├── terraform/
│   ├── main.tf          ← à compléter
│   ├── variables.tf
│   ├── outputs.tf
│   └── modules/
│       └── app-server/
│           ├── main.tf
│           └── variables.tf
└── ansible/
    ├── inventory.ini    ← à compléter
    ├── playbook.yml     ← à compléter
    └── roles/
        └── todo-api/
            ├── tasks/
            │   └── main.yml
            └── defaults/
                └── main.yml
```

---

### 📋 Étapes

#### Étape 1 — Terraform : provisionner avec des modules

Créez `terraform/modules/app-server/main.tf` :

```hcl
# Module réutilisable pour créer l'infra de l'app
terraform {
  required_providers {
    local = {
      source  = "hashicorp/local"
      version = "~> 2.4"
    }
    null = {
      source  = "hashicorp/null"
      version = "~> 3.2"
    }
  }
}

# FR : Créer la structure de répertoires de l'application
# EN : Create the application directory structure
resource "local_file" "app_config" {
  filename = "${var.output_dir}/config/${var.environment}.json"
  content  = jsonencode({
    environment = var.environment
    app_name    = var.app_name
    version     = var.app_version
    port        = var.app_port
    replicas    = var.replicas
  })
  file_permission = "0644"
}

resource "local_file" "env_file" {
  filename        = "${var.output_dir}/.env.${var.environment}"
  content         = <<-EOT
    APP_ENV=${var.environment}
    APP_VERSION=${var.app_version}
    APP_PORT=${var.app_port}
    LOG_LEVEL=${var.log_level}
  EOT
  file_permission = "0600"
}

resource "local_file" "deploy_script" {
  filename = "${var.output_dir}/scripts/deploy-${var.environment}.sh"
  content  = <<-EOT
    #!/bin/bash
    # Script de déploiement généré par Terraform
    # Environnement : ${var.environment}
    echo "Déploiement de ${var.app_name} v${var.app_version} en ${var.environment}"
    docker pull ${var.docker_image}:${var.app_version}
    docker run -d \
      --name ${var.app_name}-${var.environment} \
      -p ${var.app_port}:5000 \
      --env-file .env.${var.environment} \
      ${var.docker_image}:${var.app_version}
  EOT
  file_permission = "0755"
}
```

Créez `terraform/modules/app-server/variables.tf` :

```hcl
variable "environment" {
  description = "Nom de l'environnement (staging, production)"
  type        = string
  validation {
    condition     = contains(["staging", "production", "dev"], var.environment)
    error_message = "L'environnement doit être staging, production ou dev."
  }
}

variable "app_name"    { type = string; default = "todo-api" }
variable "app_version" { type = string; default = "1.0.0" }
variable "app_port"    { type = number; default = 5000 }
variable "replicas"    { type = number; default = 2 }
variable "log_level"   { type = string; default = "INFO" }
variable "output_dir"  { type = string; default = "./output" }
variable "docker_image"{ type = string; default = "todo-api" }
```

Créez `terraform/main.tf` :

```hcl
terraform {
  required_version = ">= 1.6"
  required_providers {
    local = { source = "hashicorp/local"; version = "~> 2.4" }
  }
}

locals {
  environments = {
    staging = {
      replicas    = 2
      app_version = "1.0.0"
      log_level   = "DEBUG"
      app_port    = 5001
    }
    production = {
      replicas    = 5
      app_version = "1.0.0"
      log_level   = "INFO"
      app_port    = 5000
    }
  }
}

# FR : Appel du module pour chaque environnement
module "app_servers" {
  for_each = local.environments
  source   = "./modules/app-server"

  environment  = each.key
  replicas     = each.value.replicas
  app_version  = each.value.app_version
  log_level    = each.value.log_level
  app_port     = each.value.app_port
  output_dir   = "${path.module}/output"
  docker_image = var.docker_image
}
```

Créez `terraform/variables.tf` :

```hcl
variable "docker_image" {
  description = "Image Docker à déployer"
  type        = string
  default     = "votre_username/todo-api"
}
```

Créez `terraform/outputs.tf` :

```hcl
output "staging_config" {
  description = "Configuration générée pour staging"
  value       = module.app_servers["staging"]
}

output "production_config" {
  description = "Configuration générée pour production"
  value       = module.app_servers["production"]
}
```

```bash
cd terraform
terraform init
terraform plan
terraform apply
ls output/config/
```

---

#### Étape 2 — Terraform Workspace (multi-environnement)

```bash
# FR : Les workspaces isolent le state par environnement
# EN : Workspaces isolate state per environment

# Créer un workspace staging
terraform workspace new staging
terraform apply -var="docker_image=votre_username/todo-api"

# Créer un workspace production
terraform workspace new production
terraform apply -var="docker_image=votre_username/todo-api"

# Lister les workspaces
terraform workspace list

# Voir le state du workspace courant
terraform state list
```

---

#### Étape 3 — Ansible : configurer avec des rôles

Créez `ansible/roles/todo-api/tasks/main.yml` :

```yaml
---
# FR : Tâches du rôle todo-api
# EN : Tasks for the todo-api role

- name: Installer les prérequis Python
  apt:
    name:
      - python3
      - python3-pip
      - curl
    state: present
    update_cache: yes
  when: ansible_os_family == "Debian"

- name: Créer le répertoire de l'application
  file:
    path: "{{ app_dir }}"
    state: directory
    owner: "{{ ansible_user }}"
    mode: "0755"

- name: Copier le fichier de configuration
  template:
    src: app.env.j2
    dest: "{{ app_dir }}/.env"
    mode: "0600"
  notify: restart todo-api

- name: Copier le script de démarrage
  copy:
    content: |
      #!/bin/bash
      cd {{ app_dir }}
      docker pull {{ docker_image }}:{{ app_version }}
      docker stop todo-api 2>/dev/null || true
      docker rm todo-api 2>/dev/null || true
      docker run -d \
        --name todo-api \
        --restart unless-stopped \
        -p {{ app_port }}:5000 \
        --env-file .env \
        {{ docker_image }}:{{ app_version }}
    dest: "{{ app_dir }}/start.sh"
    mode: "0755"

- name: Démarrer l'application
  command: "{{ app_dir }}/start.sh"
  changed_when: true

- name: Vérifier que l'application répond
  uri:
    url: "http://localhost:{{ app_port }}/health"
    status_code: 200
    timeout: 30
  retries: 5
  delay: 5
```

Créez `ansible/roles/todo-api/defaults/main.yml` :

```yaml
---
app_dir: /opt/todo-api
app_port: 5000
app_version: "1.0.0"
docker_image: "votre_username/todo-api"
app_env: "production"
log_level: "INFO"
```

Créez `ansible/playbook.yml` :

```yaml
---
- name: Configurer les serveurs d'application
  hosts: app_servers
  become: yes
  vars_files:
    - vars/{{ env }}.yml    # Charger les vars selon l'environnement

  roles:
    - role: todo-api
      tags: [deploy, app]

  post_tasks:
    - name: Vérification finale du déploiement
      uri:
        url: "http://localhost:{{ app_port }}/health"
        status_code: 200
      tags: [verify]
```

Créez `ansible/inventory.ini` :

```ini
# FR : Inventaire des serveurs cibles
# EN : Target servers inventory

[app_servers]
# FR : En local, on simule avec des conteneurs Docker
# EN : Locally, we simulate with Docker containers
localhost ansible_connection=local

[staging]
localhost ansible_connection=local

[production]
# prod-server-1 ansible_host=IP_PROD ansible_user=ubuntu ansible_ssh_private_key_file=~/.ssh/id_rsa
```

```bash
# Tester la connexion
ansible all -i ansible/inventory.ini -m ping

# Lancer le playbook en mode dry-run (--check)
ansible-playbook -i ansible/inventory.ini ansible/playbook.yml \
  --extra-vars "env=staging" --check

# Appliquer
ansible-playbook -i ansible/inventory.ini ansible/playbook.yml \
  --extra-vars "env=staging"
```

---

#### Étape 4 — Combiner Terraform et Ansible dans la pipeline

```yaml
# .github/workflows/infra.yml
name: Infrastructure Provisioning & Configuration

on:
  push:
    paths: ['terraform/**', 'ansible/**']
    branches: [main]

jobs:
  terraform:
    name: 🏗️ Terraform Plan & Apply
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: "1.6.0"
      - run: terraform -chdir=terraform init
      - run: terraform -chdir=terraform plan
      - run: terraform -chdir=terraform apply -auto-approve
        if: github.ref == 'refs/heads/main'

  ansible:
    name: ⚙️ Ansible Configuration
    runs-on: ubuntu-latest
    needs: terraform
    steps:
      - uses: actions/checkout@v4
      - run: pip install ansible
      - run: ansible-playbook -i ansible/inventory.ini ansible/playbook.yml
          --extra-vars "env=staging app_version=${{ github.sha }}"
```

---

### ☑️ Points de vérification

- [ ] `terraform init` et `terraform apply` s'exécutent sans erreur
- [ ] Le module Terraform est appelé avec `for_each` pour staging ET production
- [ ] Les workspaces Terraform isolent le state par environnement
- [ ] `ansible-playbook --check` s'exécute sans erreur (dry-run)
- [ ] L'application est accessible après le playbook Ansible
- [ ] Je comprends la différence entre provisioning (Terraform) et configuration (Ansible)

---

### 🔗 Ressources

- [Terraform modules](https://developer.hashicorp.com/terraform/language/modules)
- [Terraform workspaces](https://developer.hashicorp.com/terraform/language/state/workspaces)
- [Ansible roles](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_reuse_roles.html)
- [Ansible best practices](https://docs.ansible.com/ansible/latest/tips_tricks/ansible_tips_tricks.html)

---

## English

### 🎯 Objectives

- Provision local infrastructure with Terraform (modules, state, workspaces)
- Apply system configuration with Ansible (playbooks, roles, inventories)
- Understand the difference between provisioning (Terraform) and configuration (Ansible)
- Combine both in a complete workflow

### 📋 Steps (summary)

1. Create a reusable Terraform module `modules/app-server/`
2. Call the module with `for_each` for staging and production environments
3. Use Terraform workspaces to isolate state per environment
4. Create an Ansible role `todo-api/` with tasks, defaults and templates
5. Write a playbook that applies the role and verifies deployment
6. Configure the inventory for local (localhost) and remote targets
7. Combine Terraform + Ansible in a GitHub Actions infra pipeline

### ☑️ Checklist

- [ ] `terraform init` and `terraform apply` run without errors
- [ ] Terraform module called with `for_each` for staging AND production
- [ ] Terraform workspaces isolate state per environment
- [ ] `ansible-playbook --check` runs without errors (dry-run)
- [ ] Application accessible after Ansible playbook
- [ ] I understand the difference between provisioning and configuration
