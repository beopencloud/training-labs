# Value Stream Map — SOLUTION
# Formation DevOps Avancé · BeOpen IT · FinServ SA

## Résumé métriques DORA actuelles

| Métrique | Valeur actuelle | Niveau |
|----------|----------------|--------|
| Deployment Frequency | 1/mois | **Faible** (Élite = > 1/jour) |
| Lead Time for Changes | 3-6 semaines | **Faible** (Élite = < 1h) |
| Change Failure Rate | 35% | **Faible** (Élite = 0-15%) |
| MTTR | 4 heures | **Moyen** (Élite = < 1h) |

**Conclusion : FinServ SA est en zone "Faible" sur 3/4 métriques.**

---

## Cartographie des étapes

### Étape 1 — Rédaction du besoin métier
- **Durée** : 2 jours (réunions, spécifications)
- **Attente** : 3 jours (disponibilité Product Owner)
- **Responsable** : PO / Business analyst
- **Outils** : Confluence, email
- **Point de friction** ✅ — Spécifications incomplètes → retravail fréquent côté dev

### Étape 2 — Développement
- **Durée** : 5-10 jours
- **Attente** : 1-2 jours (dépendances entre développeurs)
- **Responsable** : Dev
- **Outils** : Git, IDE
- **Point de friction** ✅ — Branches longues (> 1 semaine) → merge conflicts à la fin

### Étape 3 — Revue de code (PR)
- **Durée** : 2-4h de review
- **Attente** : 2-3 jours (reviewer disponible)
- **Responsable** : Dev senior
- **Outils** : GitHub
- **Point de friction** ✅ — Attente longue, reviewers surchargés, PRs trop grosses

### Étape 4 — Tests manuels en recette
- **Durée** : 2-3 jours
- **Attente** : 1 jour (disponibilité QA)
- **Responsable** : QA
- **Outils** : Tests manuels, tableur Excel
- **Point de friction** ✅ — Manuel, non reproductible, erreurs humaines, lent

### Étape 5 — Validation QA et sign-off
- **Durée** : 2h
- **Attente** : 1-2 jours (manager / QA lead)
- **Responsable** : QA Lead + Manager
- **Outils** : Email, réunion
- **Point de friction** ✅ — Goulot : 1 seule personne peut signer. Bloquant si absent.

### Étape 6 — Déploiement staging
- **Durée** : 1h
- **Attente** : 2 jours (créneaux fixes)
- **Responsable** : Ops
- **Outils** : Scripts bash manuels
- **Point de friction** ✅ — Script manuel → erreurs de config, documentation inexistante

### Étape 7 — Gel de staging
- **Durée** : 0 (aucune valeur)
- **Attente** : 7 jours (gel arbitraire)
- **Responsable** : Management
- **Outils** : Calendrier
- **Point de friction** ✅✅ — 7 jours d'attente sans valeur. Convention arbitraire.

### Étape 8 — Déploiement production (vendredi soir)
- **Durée** : 2-3h
- **Attente** : jusqu'au vendredi suivant
- **Responsable** : Ops
- **Outils** : Scripts bash manuels, SSH
- **Point de friction** ✅✅ — Vendredi soir = risque max. Pas de rollback automatique.

### Étape 9 — Monitoring post-déploiement
- **Durée** : 1-2h de surveillance manuelle
- **Attente** : 0
- **Responsable** : Ops (astreinte)
- **Outils** : Logs texte, alertes email
- **Point de friction** ✅ — Pas d'observabilité structurée, détection réactive

---

## Calcul du ratio d'efficacité

```
Temps total à valeur ajoutée : ~10 jours (dev + review + tests + déploiement)
Temps total du cycle (lead time) : ~35 jours (moyenne)
Ratio d'efficacité : 10/35 × 100 = 28%
```

> Note : ce chiffre est optimiste. En réalité, beaucoup de "durées" sont du temps de coordination,
> pas de la valeur réelle. Le ratio effectif est probablement < 15%.

---

## Top 5 points de friction

1. **Gel de staging arbitraire (7 jours)** — 20% du lead time total pour 0% de valeur ajoutée
2. **Tests manuels** — Lents, non reproductibles, source d'erreurs, ralentissent chaque cycle
3. **Déploiement le vendredi soir** — Risque maximal, équipe fatiguée, support réduit le week-end
4. **Goulot du sign-off** — 1 seule personne peut approuver → bloquant en cas d'absence
5. **Branches longues + grosses PRs** — Merge conflicts coûteux, retravail fréquent

---

## Plan d'amélioration

### Horizon 1 — Quick wins (< 1 mois)
| Action | Impact | Effort |
|--------|--------|--------|
| Réduire le gel de staging à 48h max | Élevé | Faible |
| Déployer en prod le mardi matin, pas le vendredi | Élevé | Nul |
| Limiter la taille des PRs (< 300 lignes) | Moyen | Faible |
| Documenter le processus de déploiement | Moyen | Faible |

### Horizon 2 — Moyen terme (1-3 mois)
| Action | Impact | Effort |
|--------|--------|--------|
| Automatiser les tests (pytest + CI) | Élevé | Moyen |
| Mettre en place une pipeline CI/CD GitHub Actions | Élevé | Moyen |
| Automatiser le déploiement staging (docker + k8s) | Élevé | Moyen |
| Distribuer le sign-off (2 personnes habilitées) | Moyen | Faible |

### Horizon 3 — Long terme (3-6 mois)
| Action | Impact | Effort |
|--------|--------|--------|
| Déploiement continu en production | Élevé | Élevé |
| Feature flags pour rollout progressif | Élevé | Élevé |
| On-call partagé Dev + Ops | Élevé | Élevé |
| Observabilité complète (Prometheus + Grafana + Loki) | Élevé | Moyen |

---

## Métriques DORA cibles (dans 6 mois)

| Métrique | Actuel | Cible 6 mois |
|----------|--------|--------------|
| Deployment Frequency | 1/mois | 1/semaine |
| Lead Time for Changes | 3-6 sem | < 3 jours |
| Change Failure Rate | 35% | < 15% |
| MTTR | 4h | < 1h |
