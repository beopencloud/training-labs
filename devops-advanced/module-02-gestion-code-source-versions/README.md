# Module 02 — Gestion du code source, versions et collaboration

> 🇫🇷 [Français](#français) | 🇬🇧 [English](#english)

---

## Français

### 🎯 Objectifs

- Mettre en place une stratégie de branches (GitFlow vs trunk-based)
- Créer un workflow de revue de code avec Pull Request
- Gérer les versions applicatives avec tags et releases
- Générer un changelog automatique
- Configurer les règles de protection de branche

---

### 🔧 Prérequis

| Outil | Vérification |
|-------|--------------|
| Git 2.x | `git --version` |
| Compte GitHub | [github.com](https://github.com) |
| GitHub CLI (optionnel) | `gh --version` |

---

### ⏱️ Durée estimée

**1h30**

---

### 📁 Fichiers fournis

```
module-02-gestion-code-source-versions/
├── README.md
├── .gitignore
├── CHANGELOG.md             ← à compléter au fil du lab
└── solution/
    ├── .github/
    │   └── pull_request_template.md
    ├── CHANGELOG.md
    └── commands.sh
```

---

### 📋 Étapes

#### Étape 1 — Initialiser le dépôt et importer l'app fil rouge

Commencez à partir de l'application `todo-api` fournie dans ce repo :

```bash
# Créer un nouveau dépôt GitHub "todo-api-devops"
# Cloner et initialiser
git clone https://github.com/VOTRE_USERNAME/todo-api-devops.git
cd todo-api-devops

# Copier les fichiers de todo-api
cp -r ../todo-api/* .
git add .
git commit -m "feat: initial todo-api application"
git push origin main
```

---

#### Étape 2 — Comprendre les stratégies de branches

**GitFlow** — adapté aux releases planifiées :
```
main ──────────────────────────────────────── (production)
  └─ develop ──────────────────────────────── (intégration)
        ├─ feature/login ──────────────────── (fonctionnalités)
        └─ release/1.0 ────────────────────── (préparation release)
hotfix/fix-crash ──────────────────────────── (correctifs urgents)
```

**Trunk-Based Development** — adapté au déploiement continu :
```
main ──────────────────────────────────────── (unique branche longue)
  ├─ feature/login (max 1-2 jours de vie)
  └─ feature/todos (max 1-2 jours de vie)
```

> 💡 **Pour ce lab, nous utilisons GitFlow** car il est plus répandu en entreprise. En module 3, nous verrons comment adapter la pipeline CI/CD à chaque stratégie.

---

#### Étape 3 — Créer la structure de branches GitFlow

```bash
# Créer la branche develop
git checkout -b develop
git push -u origin develop

# Vérifier les branches
git branch -a
```

---

#### Étape 4 — Développer une fonctionnalité sur une branche feature

```bash
# Créer une branche feature depuis develop
git checkout develop
git checkout -b feature/add-todo-stats

# Ajouter un endpoint /stats à app.py
cat >> app.py << 'PATCH'

@app.route("/stats")
def stats():
    total = len(todos)
    done = len([t for t in todos if t["done"]])
    return jsonify({
        "total": total,
        "done": done,
        "pending": total - done
    })
PATCH

# Committer avec un message conventionnel
git add app.py
git commit -m "feat(api): add /stats endpoint for todo statistics"

# Pousser la branche
git push -u origin feature/add-todo-stats
```

> 💡 **Conventional Commits** : format `type(scope): description`
> Types : `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `ci`

---

#### Étape 5 — Créer un template de Pull Request

Créez `.github/pull_request_template.md` :

```markdown
## 📋 Description

Décrivez les changements apportés par cette PR.

## 🔗 Issue liée

Closes #___

## ✅ Checklist

- [ ] Le code compile et les tests passent localement
- [ ] J'ai ajouté/mis à jour les tests correspondants
- [ ] La documentation est à jour
- [ ] Le CHANGELOG.md est mis à jour

## 🧪 Comment tester

Décrivez comment vérifier que les changements fonctionnent.

## 📸 Captures d'écran (si applicable)
```

```bash
mkdir -p .github
# Créer le fichier template
git add .github/pull_request_template.md
git commit -m "docs: add pull request template"
git push origin feature/add-todo-stats
```

---

#### Étape 6 — Ouvrir et merger la Pull Request

1. Allez sur GitHub → **Pull requests** → **New pull request**
2. Base : `develop` ← Compare : `feature/add-todo-stats`
3. Observez que le template est pré-rempli
4. Complétez la PR et cliquez **Create pull request**
5. Faites une auto-review (ou demandez à un collègue)
6. Mergez avec **Squash and merge** pour un historique propre

---

#### Étape 7 — Protéger la branche main

Sur GitHub → Settings → Branches → **Add rule** :
- Branch name pattern : `main`
- ✅ Require a pull request before merging
- ✅ Require approvals (1 minimum)
- ✅ Require status checks to pass (on ajoutera CI au module 3)
- ✅ Do not allow bypassing the above settings

---

#### Étape 8 — Créer une release avec tag sémantique

```bash
# Depuis develop, créer une branche release
git checkout develop
git pull origin develop
git checkout -b release/1.0.0

# Mettre à jour la version dans app.py
sed -i 's/VERSION = os.environ.get("APP_VERSION", "1.0.0")/VERSION = os.environ.get("APP_VERSION", "1.0.0")/' app.py

# Mettre à jour le CHANGELOG
cat > CHANGELOG.md << 'EOF'
# Changelog

## [1.0.0] - 2026-07-06

### Added
- Initial Todo API with CRUD operations
- GET /todos — list all todos
- POST /todos — create a todo
- PUT /todos/:id — update a todo
- DELETE /todos/:id — delete a todo
- GET /stats — todo statistics
- GET /health — health check endpoint

### Technical
- Flask 3.0.3
- Structured JSON logging
- Environment-based configuration
EOF

git add CHANGELOG.md
git commit -m "chore(release): prepare release 1.0.0"

# Merger dans main
git checkout main
git merge --no-ff release/1.0.0 -m "chore: release 1.0.0"

# Créer le tag
git tag -a v1.0.0 -m "Release version 1.0.0

- Initial Todo API
- CRUD endpoints
- Stats endpoint
- Health check"

# Pousser avec le tag
git push origin main
git push origin v1.0.0

# Merger aussi dans develop
git checkout develop
git merge --no-ff release/1.0.0 -m "chore: merge release 1.0.0 back to develop"
git push origin develop

# Supprimer la branche release locale
git branch -d release/1.0.0
git push origin --delete release/1.0.0
```

---

#### Étape 9 — Créer une GitHub Release

Sur GitHub → **Releases** → **Create a release** :
- Tag : `v1.0.0`
- Title : `v1.0.0 — Initial Release`
- Description : copiez le contenu du CHANGELOG
- ✅ Set as latest release

---

#### Étape 10 — Simuler un hotfix

```bash
# Bug critique en production : un todo avec title vide crash l'API
git checkout main
git checkout -b hotfix/1.0.1-validate-title

# Corriger dans app.py (la validation existe déjà, mais ajouter un test)
cat >> test_app.py << 'PATCH'


def test_create_todo_empty_title(client):
    r = client.post("/todos", json={"title": ""})
    assert r.status_code == 400
PATCH

# Vérifier que le test révèle le bug
# python -m pytest test_app.py::test_create_todo_empty_title -v

# Corriger dans app.py
# Remplacer : if not data or "title" not in data:
# Par :       if not data or "title" not in data or not data["title"].strip():

git add .
git commit -m "fix(api): reject empty title in POST /todos"

# Merger dans main ET develop
git checkout main
git merge --no-ff hotfix/1.0.1-validate-title -m "fix: hotfix 1.0.1 empty title validation"
git tag -a v1.0.1 -m "Hotfix 1.0.1 — empty title validation"
git push origin main
git push origin v1.0.1

git checkout develop
git merge --no-ff hotfix/1.0.1-validate-title -m "fix: merge hotfix 1.0.1 back to develop"
git push origin develop

git branch -d hotfix/1.0.1-validate-title
```

---

### ☑️ Points de vérification

- [ ] Branches `main` et `develop` existent sur GitHub
- [ ] Un endpoint `/stats` a été ajouté via une branche `feature/`
- [ ] La Pull Request utilise le template `.github/pull_request_template.md`
- [ ] La branche `main` est protégée (PR obligatoire)
- [ ] Le tag `v1.0.0` est visible dans l'onglet Releases de GitHub
- [ ] Le `CHANGELOG.md` est à jour avec les changements de la v1.0.0
- [ ] Le hotfix v1.0.1 est mergé dans `main` ET `develop`
- [ ] Je comprends la différence entre GitFlow et trunk-based development

---

### 🔥 Aller plus loin

**Bonus 1** — Configurez la génération automatique de changelog avec l'action GitHub `release-drafter`.

**Bonus 2** — Ajoutez un `.github/CODEOWNERS` pour définir automatiquement les reviewers selon les fichiers modifiés.

**Réflexion** — Dans quel contexte préféreriez-vous GitFlow plutôt que trunk-based development, et vice-versa ?

---

### 🔗 Ressources

- [Conventional Commits](https://www.conventionalcommits.org/)
- [GitFlow](https://nvie.com/posts/a-successful-git-branching-model/)
- [Trunk-Based Development](https://trunkbaseddevelopment.com/)
- [Semantic Versioning](https://semver.org/)

---

---

## English

### 🎯 Objectives

- Set up a branching strategy (GitFlow vs trunk-based)
- Create a code review workflow with Pull Requests
- Manage application versions with tags and releases
- Generate a changelog
- Configure branch protection rules

### 📋 Steps (summary)

1. Initialize repo and import todo-api
2. Understand GitFlow vs trunk-based strategies
3. Create GitFlow branch structure (main + develop)
4. Develop a feature on a feature branch using Conventional Commits
5. Create a PR template in `.github/pull_request_template.md`
6. Open, review and merge a Pull Request (squash merge)
7. Protect the main branch (require PRs + approvals)
8. Create a `release/1.0.0` branch, tag `v1.0.0` and GitHub Release
9. Simulate a hotfix — branch, fix, merge to main AND develop, tag `v1.0.1`

### ☑️ Checklist

- [ ] `main` and `develop` branches exist on GitHub
- [ ] `/stats` endpoint added via a feature branch
- [ ] PR uses the `.github/pull_request_template.md` template
- [ ] `main` branch is protected (PR required)
- [ ] Tag `v1.0.0` visible in GitHub Releases tab
- [ ] `CHANGELOG.md` updated with v1.0.0 changes
- [ ] Hotfix v1.0.1 merged into both `main` and `develop`

### 🔗 Resources

- [Conventional Commits](https://www.conventionalcommits.org/)
- [GitFlow](https://nvie.com/posts/a-successful-git-branching-model/)
- [Semantic Versioning](https://semver.org/)
