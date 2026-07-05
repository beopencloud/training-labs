# Module 01 — Fondamentaux DevOps Avancés

> 🇫🇷 [Français](#français) | 🇬🇧 [English](#english)

---

## Français

### 🎯 Objectifs

- Cartographier une chaîne de delivery existante (Value Stream Mapping)
- Identifier les points de friction, goulots et gaspillages
- Mesurer les métriques DORA de référence
- Proposer un plan d'amélioration priorisé

---

### 🔧 Prérequis

Aucun outil à installer — ce lab est principalement analytique et collaboratif.

---

### ⏱️ Durée estimée

**1h30**

---

### 📁 Fichiers fournis

```
module-01-fondamentaux-devops-avances/
├── README.md
├── value-stream-template.md     ← modèle de cartographie à compléter
└── solution/
    └── value-stream-exemple.md  ← exemple complété
```

---

### 📋 Contexte du scénario

Vous êtes consultant DevOps chez **BeOpen IT**. Un client (entreprise financière fictive : **FinServ SA**) vous sollicite pour auditer leur chaîne de delivery. Voici ce qu'ils vous ont décrit :

> *"Nous avons une équipe de 8 développeurs et 3 ops. Quand une fonctionnalité est développée, elle passe en revue de code, puis en recette manuelle (2-3 jours), puis en staging (1 semaine de gel), puis en production le vendredi soir. On déploie en production environ 1 fois par mois. La dernière mise en production a causé une panne de 4 heures."*

**Métriques actuelles (fournies par le client) :**
- Lead time : 3 à 6 semaines
- Fréquence de déploiement : 1 fois/mois
- Change failure rate : 35%
- MTTR : 4 heures

---

### 📋 Étapes

#### Étape 1 — Comprendre les métriques DORA

Les 4 métriques DORA (DevOps Research and Assessment) permettent de mesurer la performance d'une équipe :

| Métrique | Description | Élite | Bien | Moyen | Faible |
|----------|-------------|-------|------|-------|--------|
| **Deployment Frequency** | Combien de fois déploie-t-on en prod ? | > 1/jour | 1/sem | 1/mois | < 6/an |
| **Lead Time for Changes** | Du commit au déploiement prod | < 1h | 1j-1sem | 1sem-1mois | > 1 mois |
| **Change Failure Rate** | % de déploiements causant un incident | 0-15% | - | 16-30% | > 30% |
| **MTTR** | Temps de rétablissement après incident | < 1h | < 24h | 1j-1sem | > 1 sem |

**Positionnez FinServ SA sur chaque métrique :**

```
Deployment Frequency : 1/mois → niveau : _______
Lead Time           : 3-6 semaines → niveau : _______
Change Failure Rate  : 35% → niveau : _______
MTTR                : 4h → niveau : _______
```

---

#### Étape 2 — Cartographier la chaîne de delivery (Value Stream Map)

Remplissez le fichier `value-stream-template.md` en listant chaque étape du processus de delivery actuel :

Pour chaque étape, notez :
- **Nom de l'étape** : ex. "Développement de la fonctionnalité"
- **Durée** : temps passé à travailler sur la tâche (value-added time)
- **Attente** : temps d'attente avant que l'étape commence
- **Responsable** : qui fait quoi (Dev / Ops / QA / Manager)
- **Outils** : outils utilisés à cette étape
- **Point de friction ?** : oui/non, et pourquoi

**Étapes à cartographier chez FinServ SA :**

1. Rédaction du besoin métier
2. Développement de la fonctionnalité
3. Revue de code (Pull Request)
4. Tests manuels en recette
5. Validation QA et sign-off
6. Déploiement en staging
7. Gel de staging (1 semaine)
8. Déploiement en production (vendredi soir)
9. Monitoring post-déploiement

---

#### Étape 3 — Identifier les points de friction

Pour chaque étape, posez-vous ces questions :

- ⏳ **Attente** : Y a-t-il des temps d'attente évitables ? (approbations, files d'attente, dépendances bloquantes)
- 🔁 **Retravail** : Des erreurs sont-elles détectées trop tard, nécessitant de revenir en arrière ?
- 🤝 **Silos** : Le passage de main entre équipes (Dev → QA → Ops) est-il fluide ou source de friction ?
- 🛠️ **Outils** : Les outils sont-ils inadaptés, manuels ou absents ?
- 📋 **Processus** : Y a-t-il des étapes sans valeur ajoutée (gel arbitraire, réunions de validation) ?

**Listez au minimum 5 points de friction identifiés.**

---

#### Étape 4 — Calculer le ratio valeur/gaspillage

```
Temps total du cycle (lead time) = somme de toutes les durées + attentes

Temps à valeur ajoutée = somme des durées où on travaille réellement

Ratio efficacité = Temps valeur ajoutée / Temps total × 100
```

> 💡 Dans la plupart des entreprises, le ratio est entre 5% et 15%. L'objectif DevOps est d'atteindre 40%+.

---

#### Étape 5 — Proposer un plan d'amélioration

Construisez un plan d'action priorisé en 3 horizons :

**Horizon 1 (Quick wins — < 1 mois) :**
- Actions à fort impact, faible effort
- Ex : automatiser les tests manuels répétitifs, réduire le gel de staging

**Horizon 2 (Moyen terme — 1 à 3 mois) :**
- Actions nécessitant un investissement modéré
- Ex : mettre en place une pipeline CI/CD, shift-left des tests

**Horizon 3 (Long terme — 3 à 6 mois) :**
- Transformation profonde
- Ex : déploiement continu, feature flags, on-call partagé Dev/Ops

---

#### Étape 6 — Présentation des résultats (10 min)

Préparez une présentation courte avec :
1. La Value Stream Map annotée
2. Les 5 principaux points de friction
3. Les métriques DORA actuelles vs cibles
4. Le plan d'amélioration en 3 horizons

---

### ☑️ Points de vérification

- [ ] Les 4 métriques DORA de FinServ SA sont positionnées sur l'échelle de performance
- [ ] La Value Stream Map liste toutes les étapes avec durées et attentes
- [ ] Au moins 5 points de friction sont identifiés et justifiés
- [ ] Le ratio efficacité est calculé
- [ ] Un plan d'amélioration en 3 horizons est rédigé

---

### 🔥 Aller plus loin

**Bonus 1** — Appliquez la même démarche à votre propre organisation. Quelles sont vos métriques DORA actuelles ?

**Bonus 2** — Recherchez le concept de **"Theory of Constraints"** (Goldratt). Comment l'appliquer à la chaîne de delivery de FinServ SA ?

**Réflexion** — Pourquoi le vendredi soir est-il le pire moment pour déployer ? Quel changement culturel permettrait d'inverser cette pratique ?

---

### 🔗 Ressources

- [DORA State of DevOps Report](https://dora.dev/research/)
- [Value Stream Mapping](https://www.lean.org/lexicon-terms/value-stream-mapping/)
- [The Phoenix Project (Gene Kim)](https://itrevolution.com/product/the-phoenix-project/)

---

---

## English

### 🎯 Objectives

- Map an existing delivery chain (Value Stream Mapping)
- Identify friction points, bottlenecks and waste
- Measure baseline DORA metrics
- Propose a prioritized improvement plan

---

### 📋 Scenario Context

You are a DevOps consultant at **BeOpen IT**. A client (**FinServ SA**, fictional financial company) asks you to audit their delivery chain:

> *"We have 8 developers and 3 ops. Features go through code review, then manual QA (2-3 days), then staging freeze (1 week), then production every Friday evening. We deploy about once a month. Our last deployment caused a 4-hour outage."*

**Current metrics:**
- Lead time: 3 to 6 weeks
- Deployment frequency: once/month
- Change failure rate: 35%
- MTTR: 4 hours

---

### 📋 Steps

#### Step 1 — Understand DORA metrics

Position FinServ SA on each DORA metric (Elite / High / Medium / Low).

#### Step 2 — Map the delivery chain

Complete `value-stream-template.md` for each stage: name, duration, wait time, owner, tools, friction point.

#### Step 3 — Identify friction points

List at least 5 friction points: unnecessary waits, rework, silos, inadequate tools, value-less steps.

#### Step 4 — Calculate the value/waste ratio

```
Efficiency ratio = Value-added time / Total cycle time × 100
```

#### Step 5 — Build an improvement plan

Three horizons: quick wins (< 1 month), medium term (1-3 months), long term (3-6 months).

#### Step 6 — Present results (10 min)

Value Stream Map · Top 5 friction points · DORA metrics · Improvement plan.

---

### ☑️ Checklist

- [ ] All 4 DORA metrics positioned on the performance scale
- [ ] Value Stream Map lists all stages with durations and wait times
- [ ] At least 5 friction points identified and justified
- [ ] Efficiency ratio calculated
- [ ] 3-horizon improvement plan written

---

### 🔗 Resources

- [DORA State of DevOps Report](https://dora.dev/research/)
- [Value Stream Mapping](https://www.lean.org/lexicon-terms/value-stream-mapping/)
