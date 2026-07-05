# 🚀 Formation DevOps Avancé — Labs pratiques

> **BeOpen IT** · Dakar, 06 Juillet 2026 · 3 jours

---

## 📋 Structure du repo

Ce repo contient les **10 labs** de la formation, organisés par module de l'agenda.  
Chaque module contient un `README.md` bilingue FR/EN avec les instructions pas à pas, les fichiers de départ et un dossier `solution/`.

```
devops-advanced/
├── module-01-fondamentaux-devops-avances/
│   └── Lab : Cartographier une chaîne de delivery et identifier les frictions
├── module-02-gestion-code-source-versions/
│   └── Lab : Workflow Git avec branche, revue, merge et release
├── module-03-pipeline-cicd/
│   └── Lab : Pipeline CI/CD complète avec GitHub Actions
├── module-04-qualite-tests-automatises/
│   └── Lab : Tests automatisés + quality gate dans la pipeline
├── module-05-packaging-artefacts-deploiement/
│   └── Lab : Construire, publier et déployer une version applicative
├── module-06-gitops-deploiements-declaratifs/
│   └── Lab : GitOps avec Argo CD
├── module-07-iac-configuration-management/
│   └── Lab : Terraform + Ansible
├── module-08-devsecops-securite-delivery/
│   └── Lab : Contrôles DevSecOps dans la pipeline
├── module-09-observabilite-feedback/
│   └── Lab : Prometheus + Grafana + Loki
└── module-10-lab-final/
    └── Lab : Chaîne DevOps complète, sécurisée et observable
```

---

## 🗂️ Structure de chaque lab

```
module-XX-nom/
├── README.md          # Instructions bilingues FR/EN
├── <fichiers de départ>
└── solution/          # Solution complète commentée
```

---

## 🚀 Démarrage rapide / Quick start

```bash
git clone https://github.com/VOTRE_USERNAME/devops-advanced.git
cd devops-advanced/module-01-fondamentaux-devops-avances
cat README.md
```

---

## 📋 Prérequis globaux / Global prerequisites

| Outil | Version | Vérification |
|-------|---------|--------------|
| Git | 2.x+ | `git --version` |
| Docker | 24.x+ | `docker --version` |
| kubectl | 1.28+ | `kubectl version --client` |
| Minikube | 1.32+ | `minikube version` |
| Helm | 3.x+ | `helm version` |
| Terraform | 1.6+ | `terraform --version` |
| Ansible | 2.15+ | `ansible --version` |
| Python | 3.10+ | `python --version` |
| Node.js | 18+ | `node --version` |

---

## 📅 Planning de la formation

| Jour | Modules | Thèmes |
|------|---------|--------|
| **Jour 1** | 1 → 4 | Fondamentaux avancés · Git · CI/CD · Qualité |
| **Jour 2** | 5 → 7 | Déploiement · GitOps · IaC + Ansible |
| **Jour 3** | 8 → 10 | DevSecOps · Observabilité · Lab final |

---

## 🏗️ Application fil rouge

Tous les labs s'appuient sur une **application Python Flask** (`todo-api`) qui évolue au fil des modules :

- Module 1-2 : code source versionné
- Module 3-4 : pipeline CI/CD + tests
- Module 5 : packaging Docker + déploiement K8s
- Module 6 : GitOps avec Argo CD
- Module 7 : infra provisionnée avec Terraform + Ansible
- Module 8 : sécurisée avec DevSecOps
- Module 9 : instrumentée avec Prometheus + Loki
- Module 10 : chaîne complète intégrée

---

## 📜 Licence

Contenu pédagogique — BeOpen IT · Usage interne formation uniquement.
