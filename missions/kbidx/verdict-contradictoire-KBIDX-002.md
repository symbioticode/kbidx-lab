# Verdict contradictoire — KBIDX-002

## Verdict indépendant

**DIVERGENT.**

Les contrôles 1 et 3 concordent avec les éléments disponibles, mais le contrôle de
preuve de clôture ne confirme pas la conclusion de l’Agent Critique.

1. `tests/verify_kb_index.py` importe bien `triplet.kb_index` et ne définit ni
   `id_line` ni `build_indexes`. Aucune duplication de logique n’a été trouvée par
   grep et vérification Python.
2. Mon test de `parse_preuve_cloture()` ne trouve aucun bloc dans
   `MISSION-KBIDX-001-verification-kb_index.md`, `mission-KBIDX-002-journal.md`,
   ni dans un bloc de code d’exemple. Résultat : aucun faux positif dans ces cas.
3. Recalcul direct depuis le disque :
   - `triplet/kb_index.py` :
     `sha256:bd983c62041644aaf468cae0de00b6b6d33de22642067942c506dbd84b5fc33e`
   - `tests/b1b7-output-kbidx002.txt` :
     `sha256:c2a19529f91c1bb6b0a2b2cd47b62087e7e022f7bbfc74a962c102bfee3c74cb`
   Les deux valeurs correspondent aux déclarations.
4. Lors d’une mutation d’un caractère du `cible_hash`, `stamp-verdict` a bien
   produit `CLOS-NON-PROUVÉ`, mais pour la raison `champs manquants`, et non pour
   `cible_hash diverge`.

### Anomalie déterminante

Dans `VERDICT-KBIDX-001bis.md`, les champs du bloc `[[preuve_cloture]]` sont
indentés. Or `PREUVE_BLOCK_RE` exige immédiatement une lettre en début de ligne :

```python
r'\[\[preuve_cloture\]\]\s*\n((?:[a-zA-Z_]+\s*=\s*.*\n)*)'
```

Le parseur retourne donc un dictionnaire vide pour le bloc réel. En conséquence,
la validation de clôture échoue actuellement même lorsque les hash déclarés sont
corrects.

## Comparaison avec le journal de l’Agent Critique

Le journal affirme :

- que le bloc réel est détecté ;
- que `stamp-verdict` a produit `CLOS` avec `PREUVE VALIDÉE` ;
- que la mutation a produit `cible_hash diverge`.

Ces trois affirmations ne sont pas reproductibles avec les fichiers présents et le
code présent. Le test indépendant a obtenu `champs manquants` dès la lecture du
bloc, y compris avec les hash corrects. Le journal semble donc provenir d’une version
où les lignes du bloc n’étaient pas indentées, ou d’un état de fichier différent.

Le journal rapporte aussi 20 tokens numériques contre 19 dans le verdict précédent;
ce point est cohérent avec le code réel et constitue un écart mineur distinct.

Le hash muté et le `KB-STATUS` ont été restaurés à leurs valeurs d’origine après le
test.
