# Checklist Lab Final — Formation DevOps Avancé
# BeOpen IT · Dakar · Juillet 2026

## Équipe : _______________________

## Code & Versioning
- [ ] Dépôt `todo-api-devops` public sur GitHub avec branches main/develop
- [ ] Au moins 1 release taguée (v1.0.0) sur GitHub Releases
- [ ] CHANGELOG.md à jour avec les changements de la v1.0.0
- [ ] Template de PR configuré dans `.github/pull_request_template.md`

## Pipeline CI/CD
- [ ] La pipeline complète passe au vert sur main (lien : _________)
- [ ] La pipeline bloque sur secret exposé (test validé)
- [ ] Coverage ≥ 80% (rapport artifact disponible)
- [ ] Image Docker sur Docker Hub (lien : _________)
- [ ] Tags `sha-*` et `latest` présents sur Docker Hub

## GitOps
- [ ] Dépôt `todo-api-config` avec structure base/ + overlays/staging/
- [ ] Argo CD installé (accessible sur https://localhost:8080)
- [ ] Application `todo-api-staging` Synced + Healthy
- [ ] Un git push déclenche automatiquement le déploiement

## Observabilité
- [ ] /metrics expose des métriques Prometheus
- [ ] Dashboard Grafana avec au moins 4 panels
- [ ] Logs visibles dans Grafana via Loki
- [ ] 2 alertes Prometheus configurées

## Sécurité
- [ ] trivy image : 0 vulnérabilité CRITICAL
- [ ] gitleaks : 0 secret exposé
- [ ] bandit : 0 finding HIGH
- [ ] Secrets GitHub configurés (non en clair)

## URL de démonstration
- Application : _______________
- Grafana : http://localhost:3000
- Prometheus : http://localhost:9090
- Argo CD : https://localhost:8080
- Docker Hub : _______________
- GitHub repo : _______________

## Notes / Difficultés rencontrées
_______________________________________________
_______________________________________________
_______________________________________________
