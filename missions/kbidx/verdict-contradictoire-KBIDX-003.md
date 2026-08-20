# Verdict contradictoire — KBIDX-003

## Verdict indépendant

**CONCORDANT sur la correction A/B ; NON-DÉTERMINABLE sur la provenance C.**

La correction minimale de `PREUVE_BLOCK_RE` accepte l’indentation réelle et ne
réintroduit pas les faux positifs testés. Le fichier réel est maintenant validé.
L’historique ayant produit les sorties du journal KBIDX-002 ne peut toutefois pas
être établi avec les artefacts présents.

## Partie A — regex et non-régression

Correction appliquée dans `tools/kb.py` :

```python
r'\[\[preuve_cloture\]\]\s*\n((?:[ \t]*[a-zA-Z_]+\s*=\s*.*\n)*)'
```

Le préfixe est limité aux espaces et tabulations ; une ligne vide ou non conforme
termine toujours la capture. `CODE_BLOCK_RE` et la restriction aux fichiers dont le
nom commence par `VERDICT-` restent inchangées.

Sorties individuelles du test négatif :

```text
MISSION-KBIDX-001-verification-kb_index.md: None
mission-KBIDX-002-journal.md: None
KBIDX-003-inline-code: None
MISSION-KBIDX-003.md: None
```

Les quatre cas sont rejetés, dont le bloc d’exemple inline et le contenu de cette
mission simulé dans un fichier `VERDICT-*`.

## Partie B — rejeu réel et mutation

Commande exécutée sur le fichier réel :

```text
$ python3 tools/kb.py stamp-verdict VERDICT-KBIDX-001bis.md --dry-run

kb.py stamp-verdict — TI-360 KB v0.2.0 (schema 0.3)
Fichier : VERDICT-KBIDX-001bis.md

[STATUT] déclaré : CLOS
[PREUVE] ✓ VALIDÉ
[STAMP]  # KB-STATUS: id=VERDICT-KBIDX-001bis status=CLOS updated=2026-08-20
[ACTION] remplacée — ancienne ligne : # KB-STATUS: id=VERDICT-KBIDX-001bis status=CLOS updated=2026-08-20

(dry-run — fichier non modifié)
```

Rejeu B1-B7 :

```text
$ python3 tests/verify_kb_index.py
by_id: 86 entités | by_term: 481 mots | by_relation: 86 entités liées
```

Mutation d’un caractère de `cible_hash` :

```text
[STATUT] déclaré : CLOS
[PREUVE] ✗ cible_hash diverge : déclaré=sha256:cd983c62041644aaf468cae0de00b6b6d33de22642067942c506dbd84b5fc33e, réel=sha256:bd983c62041644aaf468cae0de00b6b6d33de22642067942c506dbd84b5fc33e
[ACTION] Statut forcé → CLOS-NON-PROUVÉ
(dry-run — fichier non modifié)
```

Le hash et le `KB-STATUS` ont été restaurés après la mutation. La validation
directe finale était `(True, 'VALIDÉ')`.

## Partie C — clarification de provenance

Le texte fourni de la mission renvoie à un « prompt §6 », mais aucun §6 n’est
présent dans le contenu reçu : la numérotation passe de §5 à §7. Il n’était donc
pas possible de transmettre ce prompt « tel quel ».

Un second agent distinct a effectué une inspection indépendante. Ses preuves
confirment l’état actuel, mais pas l’historique :

- `validate_preuve_cloture()` retourne `(True, 'VALIDÉ')` actuellement ;
- les hash actuels correspondent aux déclarations ;
- `VERDICT-KBIDX-001bis.md` a pour hash actuel
  `10713f93aa801133ffb4fb8152971ce0e25ade8dc927656d4b308aa33b6a74ca` ;
- `stat` donne `mtime=2026-08-20 00:40:55.280620800 -0400` ;
- aucun historique exploitable n’est disponible : `.git` n’est pas un dépôt et
  aucun instantané antérieur vérifiable n’a été trouvé.

Conclusion de provenance : **NON-DÉTERMINABLE**. L’hypothèse d’une modification
entre deux exécutions reste possible, mais n’est pas prouvée ; aucune fabrication
délibérée n’est conclue.

## Partie D — écart B4 (19 vs 20)

Commande comparable sur les clés numériques de `by_term` :

```text
by_term current numeric count= 20
by_term current numeric= ['011', '100', '103', '104', '105', '126', '131', '135', '136', '168', '192', '200', '2008', '2026', '20260730', '20260802', '360', '404', '445', '600']
legacy numeric count= 20
legacy numeric= ['011', '100', '103', '104', '105', '126', '131', '135', '136', '168', '192', '200', '2008', '2026', '20260730', '20260802', '360', '404', '445', '600']
difference= []
```

Le token `011` provient de `ext-cl-2026-08-10-002`. L’explication du journal
KBIDX-002 (« ancien WORD_RE sans apostrophe ») n’est pas reproductible : les deux
regex donnent 20 clés numériques sur le corpus actuel. La cause historique exacte
de l’ancien décompte 19 est donc **NON-DÉTERMINABLE** sans l’ancien script ou un
ancien corpus.

## Résultat final

La correction de code et le rejeu local sont confirmés. La réponse de provenance
ne peut pas être transformée en explication positive ou négative faute de preuve
historique ; elle remonte **NON-DÉTERMINABLE** telle quelle.
