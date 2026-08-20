# Déclaration de fichier et registre de statut

**Statut** : ACTIF (livrable publié)
**Date** : 2026-08-14
**Type** : SYNTHESE_TRANSVERSALE — gestion de connaissance (hub KBM)
**Source de vérité** : repo git local du hub KBM ; pour un projet avec dépôt, le repo
  GitHub/GitLab du projet fait foi (cf. REPRISE.md §1)
**Justification théorique** : `drafts/2026-08-13-draft-gestion-acces-connaissance.md`
  (draft détaillé — tripartition Git contenant/contenu/sens, sentinel comme couche refs)

---

## 1. Deux besoins distincts, deux couches

Un fichier de projet répond à deux besoins différents, et chacun est porté par un objet différent.

**Le sens** — provenance, statut de vérité, chemin de preuve — est porté par les entités TI-360 (`source`, `extraction`, `decision`, `question`, `reunion`, `instance`), stockées en TOML, committées directement dans le repo comme n'importe quel fichier, et validées par `kb.py`.

**La découverte** — permettre à un script ou un agent de connaître, en un scan, le statut courant de n'importe quel fichier du repo sans avoir à parser son format — est portée par un marqueur minimal, indépendant du type de fichier.

Les deux couches ne se substituent pas l'une à l'autre. La première porte la richesse épistémique (logique de Belnap, invariants bloquants, chemin de preuve inversable). La seconde porte la visibilité opérationnelle : un registre central capable d'agréger le statut de tous les fichiers, de tous les projets, sans connaître leur format interne.

## 2. Couche sens — le modèle TI-360

Le sens n'est jamais un attribut du fichier qui le porte : c'est un objet séparé, qui référence sa source par `id`.

- **`source`** — tout artefact cristallisé (document, email, transcription, synthèse). Porte `type`, `auteur_org`, `date`, `statut`.
- **`extraction`** — l'atome de sens : une affirmation (max 50 mots), sa `source_id`, un statut de vérité à quatre valeurs (`beta` : T confirmé / F infirmé / B contradiction visible / N inconnu déclaré), un état de vérification (`verif` : NV / VC / VD / VU).
- **`decision`**, **`question`**, **`reunion`**, **`instance`** — les autres entités du graphe, chacune référençant les précédentes par `id`.

Le TOML est l'unique format source pour cette couche — jamais deux formats concurrents pour le même contenu. TOON, JSON et CSV sont des vues dérivées, générées à la demande, jamais stockées comme vérité parallèle. Le fichier TOML est committé tel quel dans le repo ; son historique de changement est celui de git, natif, sans mécanisme supplémentaire à maintenir.

## 3. Couche découverte — le marqueur `KB-STATUS`

Une ligne sentinelle, reconnaissable par une sous-chaîne littérale plutôt que par une syntaxe de commentaire — le même principe qu'un en-tête SPDX, qui fonctionne à l'identique dans n'importe quel langage ou format de fichier :

```
KB-STATUS: id=<id> status=<STATUS> updated=<YYYY-MM-DD> ref=<pointeur-optionnel>
```

Enrobée dans la syntaxe de commentaire propre à chaque fichier :

```python
# KB-STATUS: id=kb-tags-script status=ACTIVE updated=2026-08-12
```
```toml
# KB-STATUS: id=genese-chunk-000 status=DRAFT updated=2026-07-14 ref=src-genese-000-001
```
```markdown
<!-- KB-STATUS: id=ti360-architecture status=DRAFT updated=2026-08-04 -->
```

Un scanner de registre n'a besoin que d'une regex, appliquée aux N premières lignes de chaque fichier suivi par git — pas de parseur par format :

```python
KB_STATUS_RE = re.compile(r'KB-STATUS:\s*(.+)$', re.MULTILINE)
FIELD_RE     = re.compile(r'(\w+)=(\S+)')
```

**Champs** :

| Champ | Rôle |
|---|---|
| `id` | identité du fichier ou de l'entité qu'il déclare — même namespace que TI-360 (`dec-*`, `src-*`) ou un slug dédié pour les fichiers hors-KB |
| `status` | statut de fichier, vocabulaire fermé : `DRAFT \| ACTIVE \| SUPERSEDED \| ARCHIVED \| VOID` — distinct de `Decision.etat` et `Question.etat`, qui restent internes aux entités TI-360 |
| `updated` | date du dernier changement de statut ; l'historique complet reste dans `git blame` sur cette ligne, pas dans le marqueur lui-même |
| `ref` | optionnel — pointeur vers l'entité TI-360 correspondante (`chunk-000#src-genese-000-001`), quand elle existe |

**Génération plutôt qu'écriture manuelle** — pour un fichier qui est lui-même un chunk TI-360, cette ligne ne doit pas être maintenue à la main : elle doit être régénérée par un `kb.py stamp <file.toml>`, dérivée de l'état agrégé du corpus (par exemple `ACTIVE` si au moins une `question` reste `OUVERTE` ou `BLOQUANTE`, sinon dérivé du dernier `decision.etat`). C'est une vue générée, au même titre que TOON — jamais une deuxième source de vérité à resynchroniser à la main. Pour les fichiers sans entité TI-360 (code, documentation libre), la ligne reste éditée manuellement, ce qui ne pose pas de risque de dédoublement puisqu'aucune source plus riche n'existe à désynchroniser.

## 4. Règles communes aux deux couches

1. **Append-only, jamais de réécriture en place** — un état obsolète est marqué `SUPERSEDED`, jamais effacé ni remplacé silencieusement.
2. **Cycle de vie explicite, transitions déterministes, états terminaux** — un statut ne change pas librement d'une valeur à une autre ; les transitions valides sont énumérées.
3. **La transition est déclenchée par l'orchestrateur ou le validateur, jamais par l'émetteur du contenu** — un agent qui produit une extraction ne peut pas lui-même la faire passer à `CONFIRME`.
4. **Une seule source de vérité par contenu, dans un dépôt versionné, au format lisible par un humain sans outil tiers** — tout le reste (vues condensées, marqueurs de découverte, graphes, tableaux de bord) est dérivé et généré, jamais stocké comme vérité parallèle.

**Source de vérité — règle par défaut** : **GitHub (ou le repo git local)**. Pour un
contenu de projet avec dépôt, le repo GitHub/GitLab est la source de vérité et la KBM le
relie (miroir `.md` en lecture seule). Pour un contenu sans dépôt (projet mineur, KBM
elle-même), le **repo git local** fait foi. Le hub KBM est la source de vérité pour les
projets sans repo et pour le graphe qui relie les projets (REPRISE.md §1).

## 5. Exemple

Un fichier `genese-chunk-000-duo-fondements.toml`, committé dans le repo :

```toml
# KB-STATUS: id=genese-chunk-000 status=DRAFT updated=2026-08-13 ref=src-genese-000-001

[[source]]
id          = "src-genese-000-001"
titre       = "DUO — Théorie de la boucle décisionnelle, Hypothesis v0.1"
type        = "CONOPS"
statut      = "DRAFT"

[[extraction]]
id          = "ext-genese-000-001"
source_id   = "src-genese-000-001"
contenu     = "DUO est une hypothèse de travail sur la façon dont une organisation transforme ce que ses membres savent séparément en ce qu'elle décide ensemble."
type        = "DECISION"
beta        = "T"
verif       = "NV"
```

Un scanner de registre lit uniquement la ligne `KB-STATUS` pour savoir que ce fichier est `DRAFT`, mis à jour le 2026-08-13, et qu'un détail plus riche existe sous `src-genese-000-001` — sans jamais avoir besoin de charger `tomllib`. Un agent ou un humain qui veut le détail suit `ref` et va lire l'entité complète, avec son `beta`, sa source, son chemin de preuve.

## 6. Situations flaguées (ouvertes, laissées en l'état)

Les situations ci-dessous sont **déclarées et laissées ouvertes** — elles ne bloquent
pas l'adoption des sections 1-5, mais elles doivent rester visibles et non résolues
en silence (règle transverse : toute question ouverte est déclarée comme telle).

- **[FLAG-1] Révision du sens seul sans nouveau contenu** — existe-t-il un objet
  capturant une révision du sens sans changement du contenu ni nouvelle extraction ?
  Question héritée de `AND-NOTE-001` (q-and-003). Non tranchée.
- **[FLAG-2] Vérification du sens (au-delà de la structure)** — la validation
  structurelle de `kb.py validate` ne garantit pas la validation sémantique : rien ne
  vérifie qu'une `decision` répond réellement à la `question` qu'elle prétend fermer.
  Héritée de `AND-NOTE-001` (q-and-004, P5 §9.3). Non tranchée.
- **[FLAG-3] Frontière entre dépôts candidats « source de vérité »** — repo relationnel
  (`56_RELATION`) vs hub KBM (`~/TEMP/kbm-home-real`) vs repo projet : la frontière de
  périmètre entre candidats n'est pas déclarée au-delà de la règle par défaut ci-dessus.
  Non tranchée.
- **[FLAG-4] Vocabulaire de statut à harmoniser** — l'existant emploie de façon
  incohérente « Draft », « DRAFT », « Ebauche », « Approuve » ; le jeu fermé proposé
  (`DRAFT | ACTIVE | SUPERSEDED | ARCHIVED | VOID`) doit être confirmé avant
  implémentation de `kb.py stamp`. Non tranché.
- **[FLAG-5] Réglages du scanner** — N premières lignes (proposé : 20) et comportement
  multi-occurrences (plusieurs lignes `KB-STATUS` dans un même fichier). Non tranchés.
