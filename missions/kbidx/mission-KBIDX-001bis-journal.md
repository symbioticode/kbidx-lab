# JOURNAL D'EXÉCUTION — MISSION KBIDX-001

**Date :** 2026-08-19
**Agent :** OpenCode (opencode/big-pickle)
**Corpus :** 10 fichiers TOML (`corpus/all/session-*.toml`)
**Outil vérifié :** `triplet/kb_index.py` (via `tests/verify_kb_index.py` — correctif local bug ligne 54)

---

## Partie A — Préparation

### A1 — Lecture de kb_index.py

Le script (105 lignes) génère 3 index JSON depuis un corpus TOML :
- `by_id.json` — id → fichier, ligne, table, champs
- `by_term.json` — mot → {id: score de comptage}
- `by_relation.json` — graphe bidirectionnel (liens sortants + `reçoit_de` inversé)

**Bug bloquant constaté :** ligne 54 — `("id",) | REL_FIELDS | REL_LIST_FIELDS` — `TypeError: tuple ne supporte pas | avec set`. Le script ne peut pas s'exécuter.

### A2 — Corpus de test

```
corpus/all/
  session-2026-08-05-06-infra-home.toml      1 src, 2 inst, 1 run, 5 ext, 5 dec, 2 q = 16
  session-2026-08-06-graphify-variables.toml  1 src, 3 inst, 1 run, 6 ext, 3 dec, 1 q = 15
  session-2026-08-06-ia-prompts.toml          1 src, 2 inst, 1 run, 3 ext, 3 dec, 1 q = 11
  session-2026-08-06-identite-git.toml        1 src, 2 inst, 1 run, 1 ext, 1 dec, 1 q =  7
  session-2026-08-06-p0-p1.toml              1 src, 3 inst, 1 run, 2 ext, 2 dec, 2 q = 11
  session-2026-08-06-projets.toml            1 src, 2 inst, 1 run, 1 ext, 1 dec, 0 q =  6
  session-2026-08-06-retour-site.toml        1 src, 2 inst, 1 run, 6 ext, 1 dec, 0 q = 11
  session-2026-08-07-projets.toml            1 src, 2 inst, 1 run, 2 ext, 2 dec, 0 q =  7
  session-2026-08-10-client-leger-nixos.toml  2 src, 2 inst, 0 run, 8 ext, 2 dec, 0 q = 14
  session-2026-08-10-gouvernance-documentaire.toml 1 src, 2 inst, 0 run, 2 ext, 1 dec, 0 q = 6
```

**Total :** 105 lignes d'entités, 86 IDs uniques (5 IDs partagés entre fichiers : `inst-andrei` ×10, `inst-opencode` ×7, `inst-claude-code` ×3, `inst-claude-ai` ×2, `run-kbm-2026-08-06-002` ×2).

`kb.py validate` : **0 erreur, 0 avertissement** sur les 10 fichiers.

### A3 — Méthode de contournement

`tests/verify_kb_index.py` — copie de la logique `build_indexes()` avec le correctif `{"id"}` au lieu de `("id",)`. Permet de générer les index et de vérifier la logique interne sans modifier kb_index.py.

---

## Partie B — Vérifications mécaniques

### B1 — by_id.json : résolution ligne exacte

**Méthode :** Script Python indépendant qui, pour chaque entrée de by_id.json, relit la ligne indiquée et vérifie qu'elle contient `id = "<tag>"` (même logique que l'étape 4 de PROTOCOLE_TEST_verify_tags.md).

```
Résultat : 86 tags vérifiés, 0 défaut(s)
```

**Verdict B1 : PASS** — chaque entrée pointe vers la bonne ligne du bon fichier.

### B2 — by_id.json : complétude

**Méthode :** Comparaison du nombre d'entités par table (TOML brut vs by_id.json).

```
TABLE         TOML  INDEX  ECART
decision        21     21     +0
extraction      36     36     +0
instance        22      4    -18   ← duplications inst-*
question         7      7     +0
reunion          8      7     -1   ← run-kbm-2026-08-06-002 dupliqué
source          11     11     +0
TOTAL          105     86    -19
```

L'écart de 19 correspond exactement aux IDs dupliqués entre fichiers (18 instances partagées + 1 réunion dupliquée). kb_index.py déduplique correctement par dict.

**Verdict B2 : PASS** — 86/86 IDs uniques indexés. L'écart de 19 lignes est attendu (collisions documentées).

### B3 — by_term.json : exactitude du score

**Méthode :** 5 mots choisis dans les fréquences rares, comptage indépendant via `WORD_RE.findall()` (même regex que kb_index.py) sur le corpus brut.

```
'capture':  index=1, réel=1 — OK
'168':      index=1, réel=1 — OK
'103':      index=1, réel=1 — OK
'cleanup':  index=1, réel=1 — OK
'adopter':  index=1, réel=1 — OK
```

**Note :** une première vérification par `str.split().count()` donnait 4 écarts — mais c'était une erreur de la méthode de vérification (pas de kb_index.py). La tokenisation `WORD_RE.findall()` est nécessaire car elle extrait les tokens différemment de split sur espaces.

**Verdict B3 : PASS** — 0 écart avec même algorithme de tokenisation.

### B4 — by_term.json : absence de bruit

**Résultat :**
- 0 stopwords dans les clés
- 0 tokens de longueur ≤ 2
- 19 tokens numériques (IP `192`, `168`, `100`, `103`, `104`, `105`, `126`, `131`, `135`, `136`, `200`, `2008`, `2026`, `20260730`, `20260802`, `360`, `404`, `445`, `600`)
- Total : 481 mots indexés

Les tokens numériques sont du bruit réel mais bénin : ce sont des adresses IP, dates, et numéros de port extraits du champ `contenu`. Ils n'interfèrent pas avec la recherche (pas de collision sémantique).

**Verdict B4 : PASS avec réserve** — pas de stopwords, 19 tokens numériques signalés.

### B5 — by_relation.json : cohérence bidirectionnelle

**Méthode :** Vérification exhaustive sur les 86 entités : pour chaque lien sortant A→B, vérifier que B.`reçoit_de` contient A, et inversement.

```
Liens sortants sans entrant : 0
Liens entrants sans sortant : 27
```

Les 27 asymétries sont toutes de même nature : des extractions ont `decision_id` (lien sortant E→D) mais les décisions n'ont pas `extraction_ids` (pas de lien D→E dans le schéma). L'inversion crée `D.reçoit_de = [E]` mais sans lien sortant correspondant — c'est une asymétrie schématique, pas un bug de kb_index.py.

**Verdict B5 : PASS** — 0 asymétrie dans les liens sortants. Les 27 asymétries entrants sont une propriété du schéma TI-360 (extractions→décisions sans réciproque).

### B6 — Déterminisme

**Méthode :** Deux exécutions successives sur le même corpus, `diff` binaire sur les 3 fichiers JSON.

```
by_id:      IDENTICAL
by_term:    IDENTICAL
by_relation: IDENTICAL
```

**Verdict B6 : PASS** — déterminisme binairalement confirmé.

### B7 — Cas limites

| Cas | Résultat |
|---|---|
| Entrée sans champ `contenu` | Absente de by_term ✅, présente dans by_id ✅ |
| Entrée sans champ de relation | Présente dans by_relation avec uniquement `reçoit_de` ✅ |
| Corpus vide | 0, 0, 0 — pas de crash ✅ |

**Verdict B7 : PASS** — comportement correct sur tous les cas limites testés.

---

## Constats transversaux

### Bug bloquant : TypeError ligne 54

`kb_index.py` ne peut pas s'exécuter tel quel. La ligne 54 utilise `("id",) | REL_FIELDS | REL_LIST_FIELDS` — l'opérateur `|` n'est pas défini entre un tuple et un set en Python 3.12. Le correctif est `{"id"} | REL_FIELDS | REL_LIST_FIELDS` (conversion du tuple en set).

Ce bug est bloquant : aucun des 3 index ne peut être généré sans correction.

### Asymétrie schématique by_relation

Les 27 « liens entrants sans sortant » ne sont pas un bug de kb_index.py mais une propriété du schéma TI-360 : les extractions déclarent `decision_id` (lien sortant) mais les décisions ne déclarent pas `extraction_ids` (pas de lien sortant). L'inversion `reçoit_de` est correcte — elle reflète fidèlement le schéma.

### Bruit numérique dans by_term

19 tokens numériques (IP, dates) polluent l'index de termes. Impact bénin pour la navigation par mot, mais pourrait être éliminé par un filtre `word.isdigit()` dans `build_indexes()`.

---

## Métriques finales

| Métrique | Valeur |
|---|---|
| Fichiers TOML testés | 10 |
| Entités TOML totales | 105 |
| IDs uniques | 86 |
| Entités indexées (by_id) | 86 |
| Défauts résolution ligne (B1) | 0 |
| Écart complétude (B2) | 0 (19 dupliquées, attendues) |
| Écart score by_term (B3) | 0 |
| Bruit by_term (B4) | 19 tokens numériques |
| Asymétries sortantes (B5) | 0 |
| Asymétries entrantes (B5) | 27 (schéma, pas bug) |
| Déterminisme (B6) | Binairement identique |
| Cas limites (B7) | 3/3 PASS |
| Bug bloquant | 1 (TypeError ligne 54) |
