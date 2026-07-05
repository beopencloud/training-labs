#!/bin/bash
# Module 02 — Aide-mémoire des commandes Git avancées
# Formation DevOps Avancé · BeOpen IT

# --- Structure GitFlow ---
git checkout -b develop
git push -u origin develop

# --- Feature branch ---
git checkout develop
git checkout -b feature/add-todo-stats
git push -u origin feature/add-todo-stats

# --- Conventional commits ---
git commit -m "feat(api): add /stats endpoint"
git commit -m "fix(api): reject empty title"
git commit -m "docs: update CHANGELOG"
git commit -m "test: add stats endpoint tests"
git commit -m "chore(release): prepare v1.0.0"

# --- Release ---
git checkout -b release/1.0.0
git checkout main
git merge --no-ff release/1.0.0 -m "chore: release 1.0.0"
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin main --tags

# --- Hotfix ---
git checkout main
git checkout -b hotfix/1.0.1-fix-description
git checkout main && git merge --no-ff hotfix/1.0.1-fix-description
git checkout develop && git merge --no-ff hotfix/1.0.1-fix-description
git tag -a v1.0.1 -m "Hotfix 1.0.1"

# --- Inspection ---
git log --oneline --graph --all    # Visualiser toutes les branches
git tag -l                          # Lister les tags
git show v1.0.0                     # Détails d'un tag
git log --follow -p -- app.py      # Historique d'un fichier
git diff develop..feature/xxx      # Diff entre branches
