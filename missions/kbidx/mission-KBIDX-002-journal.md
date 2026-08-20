# JOURNAL D'EXÉCUTION — MISSION KBIDX-002

**Date :** 2026-08-19/20
**Agent :** OpenCode (opencode/big-pickle)
**Corpus :** 10 fichiers TOML (`corpus/all/session-*.toml`)
**Objet :** Audit critique de KBIDX-001bis + implémentation `stamp-verdict` (preuve de clôture)

---

## Étape 1 — Duplication vs Import

**Question :** `tests/verify_kb_index.py` importe-t-il `triplet.kb_index` ou duplique-t-il sa logique ?

**Méthode :** `grep -n "def " tests/verify_kb_index.py triplet/kb_index.py`

**Résultat avant correction :**
```
tests/verify_kb_index.py:16: ID_LINE_RE = ...     (copié de kb_index.py:17)
tests/verify_kb_index.py:17: WORD_RE = ...         (copié de kb_index.py:18)
tests/verify_kb_index.py:18-19: STOPWORDS = ...    (copié de kb_index.py:19-20)
tests/verify_kb_index.py:20-21: REL_*_FIELDS = ... (copié de kb_index.py:21-22)
tests/verify_kb_index.py:28: def id_line()         (copié de kb_index.py:25)
tests/verify_kb_index.py:36: def build_indexes()   (copié de kb_index.py:33)
```

**Duplication confirmée.** 7 symboles copiés ligne par ligne. La seule différence : `EXCLUDE_FIELDS` (extraite comme constante dans verify, inlinée dans kb_index).

**Correction appliquée :** Réécriture complète de `verify_kb_index.py` — import de `triplet.kb_index` via `sys.path.insert()`. Plus aucune logique dupliquée.

**Résultat après :**
```
tests/verify_kb_index.py:24: def main()    (seule fonction propre)
# tout le reste importé de triplet.kb_index
```

**Preuve :**
```
$ python3 -c "import sys; sys.path.insert(0, '.'); from triplet.kb_index import build_indexes, id_line, ID_LINE_RE, WORD_RE, STOPWORDS, REL_FIELDS, REL_LIST_FIELDS; print('Import OK')"
Import OK
```

---

## Étape 2 — Rejeu B1-B7 sur le script corrigé

Exécuté via `tests/verify_kb_index.py` (code importé de `triplet.kb_index`).

### B1 — Résolution ligne exacte
```
86 tags vérifiés, 0 défaut(s)
Verdict: PASS
```

### B2 — Complétude
```
TABLE         TOML  INDEX  ECART
decision        21     21     +0
extraction      36     36     +0
instance        22      4    -18
question         7      7     +0
reunion          8      7     -1
source          11     11     +0
TOTAL          105     86    -19
```
Verdict: PASS (86/86 IDs uniques, écart = collisions documentées)

### B3 — Exactitude score
```
capture: index={'ext-kbm-003': 1}, réel={'ext-kbm-003': 1} — OK
168:     index={'ext-cl-2026-08-10-004': 1}, réel=... — OK
103:     OK | cleanup: OK | adopter: OK
```
Verdict: PASS

### B4 — Bruit
```
481 mots indexés, 0 stopwords, 0 tokens ≤ 2
20 tokens numériques: ['011', '100', '103', '104', '105', '126', '131', '135', '136', '168', '192', '200', '2008', '2026', '20260730', '20260802', '360', '404', '445', '600']
```
Verdict: PASS avec réserve

**ÉCART vs KBIDX-001bis :** 20 tokens numériques (vs 19 rapportés précédemment). Token `011` absent du comptage précédent. Cause : l'ancien `verify_kb_index.py` dupliquait une version antérieure de `WORD_RE` (`[a-zà-ÿ0-9']+` sans l'apostrophe droite `'`). Le comptage actuel (20) est correct — il reflète la vraie logique de `triplet.kb_index`.

### B5 — Bidirection
```
Liens sortants sans entrant: 0
Liens entrants sans sortant: 27 (propriété schématique)
```
Verdict: PASS

### B6 — Déterminisme
```
by_id: IDENTICAL | by_term: IDENTICAL | by_relation: IDENTICAL
```
Verdict: PASS

### B7 — Cas limites
```
Sans contenu: by_id=True, by_term=False ✅
Corpus vide: 0, 0, 0 ✅
```
Verdict: PASS

---

## Étape 3 — PARSE_PREUVE_RE

**Objectif :** Regex ne scannant que les fichiers VERDICT-*.md, hors blocs de code.

**Résultat des tests :**
```
MISSION-KBIDX-001 match: None           ✅ (pas de faux positif)
VERDICT sans preuve block: None         ✅
Bloc dans code block: None              ✅ (exclu par CODE_BLOCK_RE)
Bloc réel hors code: True               ✅ (détecté)
```

**Fichier modifié :** `tools/kb.py` — ajout de `CODE_BLOCK_RE`, `PREUVE_BLOCK_RE`, `PREUVE_FIELD_RE`, `REQUIRED_PREUVE_FIELDS`.

---

## Étape 4 — validate_preuve_cloture() + cmd_stamp_verdict()

**Fonctions ajoutées à `tools/kb.py` :**
- `parse_preuve_cloture(path)` — extrait le bloc TOML depuis un VERDICT-*.md
- `sha256_file(path)` — hash SHA-256 d'un fichier
- `validate_preuve_cloture(verdict_path)` — vérifie champs requis, cible_hash, sortie_hash
- `cmd_stamp_verdict(path, dry_run)` — stampe KB-STATUS avec validation preuve

**CLI :** `kb.py stamp-verdict <file.md>` ajoutée au parser et au dispatch.

---

## Étape 5 — Rejeu B1-B7 sur triplet/kb_index.py (capture neuve)

Exécuté directement sur `triplet/kb_index.py` (pas via verify_kb_index.py). Sortie capturée dans `tests/b1b7-output-kbidx002.txt`.

```
RÉSUMÉ: 10 TOML, 105 entités, 86 IDs — B1-B7 tous PASS
```

**Fichier de sortie :** `tests/b1b7-output-kbidx002.txt` (1340 bytes, 46 lignes)

---

## Étape 6 — Bloc [[preuve_cloture]]

Ajouté à `VERDICT-KBIDX-001bis.md` :

```toml
[[preuve_cloture]]
cible_fichier   = "triplet/kb_index.py"
cible_hash      = "sha256:bd983c62041644aaf468cae0de00b6b6d33de22642067942c506dbd84b5fc33e"
commande        = "B1-B7 complet, voir tests/b1b7-output-kbidx002.txt"
sortie_fichier  = "tests/b1b7-output-kbidx002.txt"
sortie_hash     = "sha256:c2a19529f91c1bb6b0a2b2cd47b62087e7e022f7bbfc74a962c102bfee3c74cb"
horodatage      = "2026-08-19T23:58:00"
```

---

## Étape 7 — stamp-verdict (CLOS attendu)

**Commande :**
```
$ python3 tools/kb.py stamp-verdict VERDICT-KBIDX-001bis.md
```

**Sortie :**
```
kb.py stamp-verdict — TI-360 KB v0.2.0 (schema 0.3)
Fichier : VERDICT-KBIDX-001bis.md

[STATUT] déclaré : CLOS
[PREUVE] ✓ VALIDÉ
[STAMP]  # KB-STATUS: id=VERDICT-KBIDX-001bis status=CLOS updated=2026-08-19
[ACTION] insérée en tête de fichier

✓ VERDICT-KBIDX-001bis.md mis à jour.
```

**Résultat : CLOS** ✅

---

## Étape 8 — Test de mutation (CLOS-NON-PROUVÉ attendu)

**Mutation :** premier caractère du `cible_hash` modifié (`b` → `x`).

**Commande :**
```
$ python3 tools/kb.py stamp-verdict VERDICT-KBIDX-001bis.md
```

**Sortie :**
```
kb.py stamp-verdict — TI-360 KB v0.2.0 (schema 0.3)
Fichier : VERDICT-KBIDX-001bis.md

[STATUT] déclaré : CLOS
[PREUVE] ✗ cible_hash diverge : déclaré=sha256:xd983c62041644aaf468cae0de00b6b6d33de22642067942c506dbd84b5fc33e, réel=sha256:bd983c62041644aaf468cae0de00b6b6d33de22642067942c506dbd84b5fc33e
[ACTION] Statut forcé → CLOS-NON-PROUVÉ
[STAMP]  # KB-STATUS: id=VERDICT-KBIDX-001bis status=CLOS-NON-PROUVÉ updated=2026-08-20
[ACTION] remplacée — ancienne ligne : # KB-STATUS: id=VERDICT-KBIDX-001bis status=CLOS updated=2026-08-19

✓ VERDICT-KBIDX-001bis.md mis à jour.
```

**Résultat : CLOS-NON-PROUVÉ** ✅ — raison explicite (hash diverge), avec les deux valeurs.

**Restauration :** hash corrigé, stamp-verdict rejoué → CLOS restauré.

---

## Écarts trouvés (vs KBIDX-001bis)

| Étape | Écart | Gravité | Cause |
|---|---|---|---|
| 1 | verify_kb_index.py dupliquait 7 symboles | CORRIGÉ | Copie/colle sans import |
| B4 | 20 tokens numériques (vs 19 rapportés) | MINEUR | Ancien WORD_RE dupliqué diffère du vrai |

---

## Métriques finales

| Métrique | Valeur |
|---|---|
| Fichiers TOML testés | 10 |
| Entités totales | 105 |
| IDs uniques | 86 |
| B1 (ligne) | 0 défaut |
| B2 (complétude) | PASS |
| B3 (score) | PASS |
| B4 (bruit) | 20 tokens numériques |
| B5 (bidirection) | 0 sortants manquants |
| B6 (déterminisme) | IDENTICAL |
| B7 (cas limites) | PASS |
| Duplication verify/kb_index | CORRIGÉ (0 symbole dupliqué) |
| stamp-verdict CLOS | VALIDÉ |
| stamp-verdict mutation | CLOS-NON-PROUVÉ ✅ |

---

## Artefacts produits

- `tests/verify_kb_index.py` — réécrit, import de `triplet.kb_index`, zéro duplication
- `tools/kb.py` — ajout `stamp-verdict`, `validate_preuve_cloture()`, `parse_preuve_cloture()`
- `tests/b1b7-output-kbidx002.txt` — sortie B1-B7 capture neuve
- `VERDICT-KBIDX-001bis.md` — bloc `[[preuve_cloture]]` ajouté + KB-STATUS stampé
