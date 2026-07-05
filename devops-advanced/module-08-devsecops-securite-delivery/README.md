# Module 08 — DevSecOps et sécurité du delivery

> 🇫🇷 [Français](#français) | 🇬🇧 [English](#english)

---

## Français

### 🎯 Objectifs

- Intégrer les contrôles de sécurité dans la pipeline CI/CD (Shift Left Security)
- Détecter les secrets exposés dans le code avec `gitleaks`
- Scanner les dépendances vulnérables avec `safety` et `pip-audit`
- Scanner les images Docker avec `Trivy`
- Signer et vérifier les artefacts avec `Cosign`
- Configurer un quality gate de sécurité bloquant

---

### 🔧 Prérequis

| Outil | Vérification |
|-------|--------------|
| Module 03 terminé | Pipeline CI/CD opérationnelle |
| Docker | `docker --version` |
| Trivy | [Installation](https://trivy.dev/latest/getting-started/installation/) |

---

### ⏱️ Durée estimée

**2h**

---

### 📁 Fichiers fournis

```
module-08-devsecops-securite-delivery/
├── README.md
├── .gitleaks.toml          ← configuration gitleaks
└── solution/
    └── .github/workflows/
        └── devsecops.yml   ← pipeline DevSecOps complète
```

---

### 📋 Étapes

#### Étape 1 — Comprendre le Shift Left Security

```
Traditionnel :
Dev → Build → Test → Staging → ✅/❌ Audit sécurité → Prod
                                         ↑
                              Problèmes détectés très tard

DevSecOps (Shift Left) :
Dev → 🔒Secrets scan → Build → 🔒Deps scan → 🔒Image scan → Test → Prod
↑               ↑                       ↑                ↑
git hook      lint step          pipeline step     gate bloquant
```

**Plus tôt un problème est détecté, moins il coûte à corriger.**

---

#### Étape 2 — Scanner les secrets exposés (gitleaks)

```bash
# Installer gitleaks
# macOS: brew install gitleaks
# Linux: télécharger depuis https://github.com/gitleaks/gitleaks/releases

# Scanner le dépôt entier
gitleaks detect --source . --verbose

# Scanner uniquement les nouveaux commits (pour le pre-commit hook)
gitleaks protect --staged --verbose
```

Créez `.gitleaks.toml` pour personnaliser :

```toml
title = "BeOpen IT — Gitleaks configuration"

[extend]
useDefault = true

[[rules]]
id = "beopen-api-key"
description = "BeOpen IT internal API key"
regex = '''BEOPEN_[A-Z0-9]{32}'''
tags = ["api-key", "beopen"]

[allowlist]
description = "Autoriser les valeurs de test"
regexes = [
  '''example-token''',
  '''VOTRE_TOKEN_ICI''',
]
```

**Configurer le pre-commit hook :**

```bash
# .git/hooks/pre-commit
#!/bin/bash
gitleaks protect --staged --verbose
if [ $? -ne 0 ]; then
    echo "❌ Secrets détectés — commit bloqué !"
    exit 1
fi
```

---

#### Étape 3 — Scanner les dépendances vulnérables

```bash
pip install safety pip-audit

# Scanner avec safety
safety check --json > safety-report.json
cat safety-report.json

# Scanner avec pip-audit (plus précis, source OSV)
pip-audit --format=json --output=pip-audit-report.json
pip-audit  # Version lisible

# Vérifier que flask n'a pas de CVE critique
pip-audit --package flask
```

---

#### Étape 4 — Scanner l'image Docker avec Trivy

```bash
# Installer Trivy
# macOS: brew install trivy
# Linux: curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh

# Scanner l'image locale
docker build -t todo-api:scan .
trivy image todo-api:scan

# Scanner uniquement les vulnérabilités CRITICAL et HIGH
trivy image --severity CRITICAL,HIGH todo-api:scan

# Générer un rapport JSON
trivy image --format json --output trivy-report.json todo-api:scan

# Scanner le Dockerfile (bonne pratique avant même de builder)
trivy config Dockerfile

# Scanner le filesystem (dépendances Python)
trivy fs --scanners vuln .
```

---

#### Étape 5 — Signer l'image avec Cosign

```bash
# Installer Cosign
# macOS: brew install cosign
# Linux: https://docs.sigstore.dev/cosign/system_config/installation/

# Générer une paire de clés
cosign generate-key-pair
# Génère cosign.key (privée) et cosign.pub (publique)

# Signer l'image après le push sur Docker Hub
IMAGE="VOTRE_USERNAME/todo-api:latest"
cosign sign --key cosign.key $IMAGE

# Vérifier la signature
cosign verify --key cosign.pub $IMAGE

# Vérifier la signature dans la pipeline (étape de validation)
cosign verify \
  --key https://raw.githubusercontent.com/VOTRE_USERNAME/todo-api/main/cosign.pub \
  $IMAGE
```

> ⚠️ **Ne jamais committer `cosign.key`** — ajoutez-la dans les secrets GitHub.

---

#### Étape 6 — Quality gate DevSecOps dans la pipeline

Créez `.github/workflows/devsecops.yml` :

```yaml
name: DevSecOps Security Pipeline

on:
  push:
    branches: [main, develop, 'feature/**']
  pull_request:
    branches: [main]

jobs:
  # ── Contrôle 1 : Secrets ────────────────────────────────────────────────
  secrets-scan:
    name: 🔐 Secrets Scan (gitleaks)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0   # Historique complet pour gitleaks

      - uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

  # ── Contrôle 2 : Dépendances ────────────────────────────────────────────
  deps-scan:
    name: 📦 Dependency Scan (pip-audit)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Installer les outils
        run: pip install pip-audit safety flask

      - name: Scanner les dépendances (pip-audit)
        run: |
          pip-audit --format=json --output=pip-audit-report.json
          pip-audit  # Afficher les résultats lisibles

      - name: Scanner avec safety
        run: safety check
        continue-on-error: true

      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: dependency-reports-${{ github.sha }}
          path: pip-audit-report.json

  # ── Contrôle 3 : Image Docker ───────────────────────────────────────────
  image-scan:
    name: 🐳 Image Scan (Trivy)
    runs-on: ubuntu-latest
    needs: [secrets-scan, deps-scan]
    steps:
      - uses: actions/checkout@v4

      - name: Build image pour scan
        run: docker build -t todo-api:scan .

      - name: Scanner avec Trivy
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: todo-api:scan
          format: sarif
          output: trivy-results.sarif
          severity: CRITICAL,HIGH
          exit-code: 1   # Bloquer si CRITICAL ou HIGH trouvé

      - name: Upload résultats au GitHub Security tab
        uses: github/codeql-action/upload-sarif@v3
        if: always()
        with:
          sarif_file: trivy-results.sarif

  # ── Contrôle 4 : Analyse statique sécurité ─────────────────────────────
  sast:
    name: 🔍 SAST (bandit)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - run: pip install bandit

      - name: Analyse de sécurité du code
        run: |
          bandit -r app.py -f json -o bandit-report.json
          bandit -r app.py -ll   # Afficher findings MEDIUM+ 

      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: sast-report-${{ github.sha }}
          path: bandit-report.json

  # ── Résumé security gate ────────────────────────────────────────────────
  security-gate:
    name: 🛡️ Security Gate Summary
    runs-on: ubuntu-latest
    needs: [secrets-scan, deps-scan, image-scan, sast]
    if: always()
    steps:
      - name: Résumé du security gate
        run: |
          echo "## 🛡️ DevSecOps Security Gate Results" >> $GITHUB_STEP_SUMMARY
          echo "| Check | Status |" >> $GITHUB_STEP_SUMMARY
          echo "|-------|--------|" >> $GITHUB_STEP_SUMMARY
          echo "| Secrets scan (gitleaks) | ${{ needs.secrets-scan.result == 'success' && '✅' || '❌' }} |" >> $GITHUB_STEP_SUMMARY
          echo "| Dependency scan (pip-audit) | ${{ needs.deps-scan.result == 'success' && '✅' || '⚠️' }} |" >> $GITHUB_STEP_SUMMARY
          echo "| Image scan (Trivy) | ${{ needs.image-scan.result == 'success' && '✅' || '❌' }} |" >> $GITHUB_STEP_SUMMARY
          echo "| SAST (bandit) | ${{ needs.sast.result == 'success' && '✅' || '⚠️' }} |" >> $GITHUB_STEP_SUMMARY
```

---

#### Étape 7 — Tester le security gate

**Test 1 : Exposer un faux secret**

```bash
# Ajouter temporairement une fausse clé API dans app.py
echo "API_KEY = 'AKIAIOSFODNN7EXAMPLE'" >> app.py
git add app.py
git commit -m "test: intentional secret exposure"
git push origin develop
```

> ✅ gitleaks doit détecter le secret et bloquer la pipeline.

**Test 2 : Utiliser une dépendance vulnérable**

```bash
# Ajouter une ancienne version vulnérable
echo "flask==0.12.0" >> requirements.txt
git add requirements.txt
git commit -m "test: vulnerable dependency"
git push origin develop
```

> ✅ pip-audit doit signaler les CVE.

**Dans les deux cas, corrigez et re-poussez pour revenir au vert.**

---

### ☑️ Points de vérification

- [ ] `gitleaks detect` ne trouve aucun secret dans le dépôt
- [ ] `pip-audit` ou `safety check` s'exécutent sans vulnérabilité CRITICAL
- [ ] `trivy image` ne retourne aucune vulnérabilité CRITICAL sur l'image
- [ ] `bandit -r app.py` ne retourne aucun finding HIGH
- [ ] La pipeline bloque si un secret est exposé (gitleaks-action)
- [ ] Les rapports de sécurité sont uploadés dans les artifacts et/ou le Security tab

---

### 🔗 Ressources

- [Gitleaks](https://github.com/gitleaks/gitleaks)
- [Trivy](https://trivy.dev/)
- [pip-audit](https://pypi.org/project/pip-audit/)
- [Bandit](https://bandit.readthedocs.io/)
- [Cosign / Sigstore](https://docs.sigstore.dev/)
- [OWASP DevSecOps Guideline](https://owasp.org/www-project-devsecops-guideline/)

---

## English

### 🎯 Objectives

- Integrate security controls into the CI/CD pipeline (Shift Left Security)
- Detect exposed secrets with `gitleaks`
- Scan vulnerable dependencies with `safety` and `pip-audit`
- Scan Docker images with `Trivy`
- Sign and verify artifacts with `Cosign`
- Configure a blocking security quality gate

### 📋 Steps (summary)

1. Understand Shift Left Security: detect issues earlier in the pipeline
2. Configure and run gitleaks to scan for exposed secrets
3. Scan dependencies with pip-audit and safety
4. Scan the Docker image with Trivy (CRITICAL + HIGH severity)
5. Sign the image with Cosign after push
6. Create a complete DevSecOps pipeline with 4 parallel security checks
7. Test the gate by intentionally exposing a fake secret and a vulnerable dependency

### ☑️ Checklist

- [ ] `gitleaks detect` finds no secrets in the repository
- [ ] `pip-audit` runs without CRITICAL vulnerabilities
- [ ] `trivy image` returns no CRITICAL vulnerabilities
- [ ] `bandit -r app.py` returns no HIGH findings
- [ ] Pipeline blocks when a secret is exposed (gitleaks-action)
- [ ] Security reports uploaded to artifacts and/or Security tab
