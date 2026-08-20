# MISSION — KBIDX-001 — Vérification de kb_index.py (by_id / by_term / by_relation)

## 0. Métadonnées
Mission ID : KBIDX-001
Date de création : 2026-08-19
Auteur / Agent : Andrei (commanditaire) — agent exécutant à assigner (Codex, OpenCode, ou autre)
Projet : Index triples KBM (extension de 68_CTAGS-KB / kb_tags.py)
Statut : ACTIF
Source de vérité : repo de test local, hors KBM — même convention que PROTOCOLE_TEST_verify_tags.md
(`/home/andrei/Projects/68_CTAGS-KB` ou équivalent dédié, à confirmer par l'agent au démarrage)

## 1. Contexte

`kb_tags.py` a déjà été testé et validé (voir VERDICT.md, PROTOCOLE_TEST_verify_tags.md) : il
produit une navigation id → ligne, déterministe, stdlib, mais suppose que l'id est déjà connu.

`kb_index.py` (livré, jamais testé) éclate le même corpus TOML en trois vues dérivées :
- `by_id.json` — équivalent JSON de ce que fait déjà kb_tags.py (id → fichier, ligne, champs)
- `by_term.json` — concordance : mot du champ `contenu` → {id: score de comptage}
- `by_relation.json` — graphe d'adjacence bidirectionnel (liens sortants déclarés dans le TOML
  + liens entrants "reçoit_de" reconstruits par inversion)

Aucun des trois fichiers n'a été vérifié empiriquement. Le script n'a tourné que sur un exemple
illustratif dans la conversation qui l'a produit — jamais sur le corpus réel.

Le TOML reste l'unique source de vérité (principe DUO : documents = vues, jamais sources).
Les trois JSON sont des vues dérivées, régénérables, jamais éditées à la main.

## 2. Objectif général

Établir, avec preuves à l'appui (pas d'affirmation non vérifiée), si `kb_index.py` produit des
index corrects, complets et déterministes sur le corpus KBM réel — sur le modèle exact du
protocole déjà appliqué à `kb_tags.py`.

## 3. Objectifs détaillés
- Vérifier que `by_id.json` est mécaniquement correct (même niveau d'exigence que le protocole
  ctags déjà validé : chaque entrée pointe vers la bonne ligne du bon fichier).
- Vérifier que `by_term.json` est complet et que les scores sont exacts (pas juste plausibles).
- Vérifier que `by_relation.json` est bidirectionnellement cohérent (tout lien sortant a son
  lien entrant correspondant, et vice-versa).
- Vérifier le déterminisme : deux exécutions sur le même corpus produisent un JSON identique
  (test explicitement absent du protocole ctags original — nouveau ici).
- Documenter tout écart, même mineur, sans le corriger de sa propre initiative.

## 4. Protocole à observer

### Setup
- Copier `kb_index.py` et le corpus de test réel (les mêmes fichiers TOML utilisés pour valider
  kb_tags.py : `session-2026-08-*.toml`, ou un sous-ensemble représentatif) hors KBM, dans le
  répertoire de test.
- `python3` avec `tomllib` (stdlib, Python ≥ 3.11) — aucune dépendance externe à installer.
- Ne pas committer dans le hub KBM : ce test reste local, comme 68_CTAGS-KB.

### Métriques à capter
1. Nombre d'entités indexées dans `by_id` — doit correspondre exactement au total rapporté par
   `kb.py validate` sur le même corpus (source, instance, reunion, extraction, decision, question).
2. Nombre de défauts de résolution ligne dans `by_id` (id → ligne incorrecte).
3. Nombre de mots dans `by_term` dont le score déclaré diverge du compte réel (vérification par
   grep indépendant sur `contenu`).
4. Nombre d'asymétries dans `by_relation` (lien sortant sans `reçoit_de` correspondant, ou
   inversement).
5. Résultat du test de déterminisme (diff binaire entre deux générations successives).

## 5. Procédure / Étapes

### Partie A — Préparation
- Lire entièrement `kb_index.py` avant tout test (pas de confiance a priori sur le docstring).
- Confirmer la liste exacte des fichiers TOML du corpus de test et leur nombre d'entités attendu
  (rejouer `kb.py validate` sur chacun si besoin, pour avoir un chiffre de référence indépendant).

### Partie B — Vérifications mécaniques (adapter le protocole déjà validé sur kb_tags.py)

**B1 — `by_id.json` : résolution ligne exacte**
Pour chaque entrée, relire la ligne indiquée dans le fichier source et vérifier qu'elle contient
bien `id = "<tag>"`. Script Python indépendant, sur le modèle de l'étape 4 de
PROTOCOLE_TEST_verify_tags.md (ne pas réutiliser la logique interne de kb_index.py pour se
vérifier elle-même — c'est le même piège que l'épisode CODEX/OPENCODE documenté dans
RAPPORT_SITUATION_2026-08-12.md).

**B2 — `by_id.json` : complétude**
Compter les entrées de `by_id` par table (`source`, `extraction`, `decision`, etc.) et comparer
au compte donné par `kb.py validate` sur le même fichier. Tout écart est un défaut à documenter,
pas à expliquer par hypothèse.

**B3 — `by_term.json` : exactitude du score**
Choisir 5 mots au hasard dans `by_term` (pas les plus fréquents — un échantillon qui inclut des
mots rares). Pour chacun, `grep -o` le mot dans les champs `contenu` du corpus et compter les
occurrences réelles par id. Comparer au score stocké.

**B4 — `by_term.json` : absence de bruit**
Vérifier qu'aucune clé de `by_term` n'est un stopword (la liste `STOPWORDS` du script est
volontairement minimale et français uniquement — noter explicitement si des mots anglais ou des
tokens numériques polluent l'index ; ne pas corriger, seulement flaguer, voir §8).

**B5 — `by_relation.json` : cohérence bidirectionnelle**
Pour chaque entrée A avec un lien sortant vers B (`decision_id`, `source_id`, etc.), vérifier
que `by_relation[B]["reçoit_de"]` contient A. Script de vérification croisée, exhaustif sur
toutes les entrées, pas un échantillon.

**B6 — Déterminisme**
Exécuter `kb_index.py` deux fois de suite sur le même corpus, dans deux répertoires de sortie
distincts. `diff` les trois paires de fichiers JSON. Écart attendu : aucun (sort_keys=True côté
by_id/by_relation ; vérifier que by_term l'est aussi puisque les dict Python ≥3.7 préservent
l'ordre d'insertion, qui peut varier selon l'ordre de lecture des fichiers d'entrée).

**B7 — Cas limites**
Tester sur une entrée sans champ `contenu` (ne doit pas planter, ne doit rien ajouter à
by_term), et sur une entrée sans aucun champ de `REL_FIELDS`/`REL_LIST_FIELDS` (ne doit pas
apparaître dans by_relation, ou y apparaître vide — documenter le comportement réel observé).

### Partie C — Rejeu de régression
Toute modification future de `kb_index.py` (format de sortie, champs indexés, stopwords) doit
rejouer B1 à B7 intégralement. Aucune modification n'est exemptée.

## 6. Ce que l'agent doit faire
1. Exécuter les étapes B1 à B7 dans l'ordre, sur le corpus réel confirmé en Partie A.
2. Consigner chaque résultat factuellement — nombre de défauts trouvés, pas d'interprétation
   prématurée sur leur cause tant qu'elle n'est pas vérifiée à la source.
3. Si un écart est trouvé, vérifier sa cause réelle (lire le code, ne pas supposer), mais ne
   corriger `kb_index.py` sous aucun prétexte sans validation explicite d'Andrei.
4. Produire deux livrables (voir §10) : un journal d'exécution factuel et un verdict de synthèse
   sur le modèle exact de VERDICT.md.
5. Si les résultats sont insuffisants pour trancher (corpus trop petit, cas non couvert),
   le déclarer explicitement plutôt que d'extrapoler.

## 7. Critères de succès
- [ ] B1 à B7 exécutées intégralement, aucune étape sautée ou résumée
- [ ] Chaque défaut trouvé documenté avec preuve reproductible (commande exacte, sortie brute)
- [ ] Test de déterminisme (B6) exécuté et son résultat rapporté sans ambiguïté
- [ ] Aucune modification de `kb_index.py` effectuée sans validation d'Andrei
- [ ] Verdict final formulé au même niveau de rigueur que VERDICT.md (valeur réelle vs marginale
      vs nulle, par sous-composant — pas un verdict global unique qui masquerait un écart
      ponctuel)

## 8. Interdictions
- Ne pas corriger `kb_index.py` de sa propre initiative, même pour un défaut évident
- Ne pas committer les fichiers de test dans le hub KBM
- Ne pas fusionner ou remplacer `kb_tags.py` — les deux coexistent, l'un ne teste pas la valeur
  de l'autre
- Ne pas se prononcer sur l'utilité d'un thésaurus (couche conceptuelle) — hors scope de cette
  mission, question distincte non tranchée
- Ne pas conclure sur la Phase 2 (L0/L1/L2) à partir de ce test — cette mission valide la
  justesse mécanique des index, pas leur usage réel en navigation agentique

## 9. Placeholders réutilisables
[CHECKLIST_LOCAL] : voir §7
[DECISION_CRITIQUE] : tout défaut trouvé en B1-B7 est une décision à faire remonter à Andrei,
  pas à trancher seul
[KBM_ENTRY] : aucune — hors KBM tant que le verdict n'est pas rendu
[LOG_ENTRY] : une ligne par étape B1-B7, horodatée, dans le journal d'exécution

## 10. Format attendu
Rapport de mission : `mission-KBIDX-001-journal.md` (log factuel étape par étape, commandes et
sorties brutes incluses)
Livrables :
- `VERDICT-KBIDX-001.md` (synthèse finale, format VERDICT.md)
- `by_id.json`, `by_term.json`, `by_relation.json` générés sur le corpus de test
- Scripts de vérification indépendants utilisés pour B1-B6 (committés à part, pour rejeu futur)
