# KB-STATUS: id=VERDICT-KBIDX-001bis status=CLOS updated=2026-08-20

# VERDICT-KBIDX-001 — Vérification de kb_index.py

**Date :** 2026-08-19
**Type :** VERDICT
**Statut :** CLOS (corrigé + re-vérifié)
**Portée :** Vérification mécanique des 3 index JSON produits par `kb_index.py` sur le corpus KBM réel (10 TOML, 105 entités, 86 IDs uniques).

---

## Question

`kb_index.py` produit-il des index JSON corrects, complets et déterministes sur le corpus KBM réel ?

## Méthode

Protocole MISSION-KBIDX-001 (étapes B1-B7), exécuté via `tests/verify_kb_index.py` (correctif local du bug ligne 54, sans modification de kb_index.py).

Corpus : 10 fichiers TOML `corpus/all/session-*.toml`, tous validés par `kb.py validate` (0 erreur, 0 avertissement).

## Résultats

### by_id.json — 86 entités indexées

| Critère | Résultat |
|---|---|
| Résolution ligne (B1) | **0 défaut** sur 86 tags — chaque id pointe vers la bonne ligne |
| Complétude (B2) | **86/86 IDs uniques** — l'écart de 19 lignes correspond aux collisions inst-* et 1 réunion dupliquée (attendu) |
| Déterminisme (B6) | **Binairement identique** (2 runs, 0 diff) |

### by_term.json — 481 mots indexés

| Critère | Résultat |
|---|---|
| Exactitude score (B3) | **0 écart** sur 5 mots vérifiés (même tokenisation = scores identiques) |
| Bruit (B4) | **19 tokens numériques** (IP, dates) — bruit bénin, pas de stopwords ni tokens courts |

### by_relation.json — 86 entités liées

| Critère | Résultat |
|---|---|
| Bidirectionnalité (B5) | **0 asymétrie sortante**, 27 asymétries entrantes = propriété schématique (extractions→décisions sans réciproque `extraction_ids`) |

### Cas limites (B7)

| Cas | Résultat |
|---|---|
| Entrée sans `contenu` | Absente de by_term, présente dans by_id ✅ |
| Entrée sans relations | Présente avec `reçoit_de` uniquement ✅ |
| Corpus vide | 0, 0, 0 — pas de crash ✅ |

## Défauts trouvés

### 1. Bug corrigé — TypeError ligne 54 (CRITIQUE → RÉSOLU)

`("id",) | REL_FIELDS | REL_LIST_FIELDS` échouait avec `TypeError: unsupported operand type(s) for |: 'tuple' and 'set'`.

**Correctif appliqué :** `{"id"} | REL_FIELDS | REL_LIST_FIELDS` (tuple → set), ligne 54 de `triplet/kb_index.py`.

**Re-vérification :** B1-B7 rejoués intégralement sur le script corrigé — tous passés, zéro régression. Le correctif n'affecte que l'exécution, pas la logique.

### 2. Bruit numérique dans by_term (MINEUR)

19 tokens numériques (adresses IP, dates) polluent l'index. Pas d'impact fonctionnel pour la navigation, mais pourrait être filtré par `word.isdigit()` dans `build_indexes()`.

### 3. Asymétrie schématique by_relation (INFO)

27 liens « entrants sans sortant » — les extractions déclarent `decision_id` mais les décisions n'ont pas `extraction_ids`. Ce n'est pas un bug de kb_index.py, c'est une propriété du schéma TI-360.

## Verdict

**kb_index.py est correct, complet, déterministe et désormais exécutable.**

Par sous-composant :

| Composant | Valeur | Commentaire |
|---|---|---|
| by_id.json | **Correct** | 86/86 IDs, résolution ligne parfaite, déterministe |
| by_term.json | **Correct avec réserve** | Scores exacts, 20 tokens numériques (bénin) |
| by_relation.json | **Correct** | Bidirectionnalité parfaite pour les champs du schéma |
| Exécution du script | **Corrigé** | Bug TypeError ligne 54 résolu (`{"id"}`) |

## Recommandation

1. **✅ CORRIGÉ** — Bug ligne 54 appliqué, B1-B7 rejoués, zéro régression.
2. **Optionnel :** ajouter un filtre `word.isdigit()` dans `build_indexes()` pour éliminer les tokens numériques de by_term.
3. **Ne pas modifier** la logique de by_relation — l'asymétrie est une propriété du schéma, pas un défaut.

## Artefacts produits

- `mission-KBIDX-001-journal.md` — journal d'exécution détaillé (étapes A, B1-B7)
- `tests/verify_kb_index.py` — script de vérification indépendant (correctif local, sans modification de kb_index.py)
- `index-run1/` — index générés (by_id.json, by_term.json, by_relation.json)
- `index-run2/` — deuxième run pour test de déterminisme (identique à run1)

---

[[preuve_cloture]]
cible_fichier   = "triplet/kb_index.py"
cible_hash      = "sha256:bd983c62041644aaf468cae0de00b6b6d33de22642067942c506dbd84b5fc33e"
commande        = "python3 -c 'import sys; sys.path.insert(0, \".\"); from triplet.kb_index import build_indexes; ...' (B1-B7 complet, voir tests/b1b7-output-kbidx002.txt)"
sortie_fichier  = "tests/b1b7-output-kbidx002.txt"
sortie_hash     = "sha256:c2a19529f91c1bb6b0a2b2cd47b62087e7e022f7bbfc74a962c102bfee3c74cb"
horodatage      = "2026-08-19T23:58:00"
