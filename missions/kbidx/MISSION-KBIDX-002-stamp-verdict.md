# MISSION — KBIDX-002 — kb.py stamp-verdict + correction des défauts identifiés

## 0. Métadonnées
Mission ID : KBIDX-002
Date de création : 2026-08-19
Auteur / Agent : Andrei (commanditaire) — deux agents exécutants requis (voir §4-§5)
Projet : Index triples KBM — couche preuve de clôture (extension de KBIDX-001)
Statut : ACTIF
Source de vérité : repo de test local, hors KBM — `/home/andrei/Projects/68_CTAGS-KB` ou
équivalent confirmé au démarrage

## 1. Contexte

La revue KBIDX-001bis via PAMD a produit un plan d'implémentation (`kb.py stamp-verdict` +
bloc `[[preuve_cloture]]`) globalement solide, mais deux défauts ont été identifiés avant tout
codage :

1. **Défaut bloquant** — le plan valide qu'un hash correspond à un fichier de sortie, jamais
   que ce fichier provient réellement de l'exécution de `triplet/kb_index.py`.
   `tests/verify_kb_index.py` est décrit (journal KBIDX-001, Partie A3) comme une **copie** de
   la logique interne, pas un appel du code réel. Si c'est toujours le cas, tout le mécanisme
   de preuve validerait cryptographiquement un fait vrai mais hors sujet.
2. **Défaut mineur** — `PARSE_PREUVE_RE` cherchant `[[preuve_cloture]]` par sous-chaîne risque
   de matcher un bloc d'exemple dans la documentation (ce fichier-ci en contient un).

Consigne explicite pour cette mission : **les deux défauts sont corrigés maintenant**, pas
reportés comme dette technique v2. « Acceptable en v1 » a été refusé comme réponse.

## 2. Objectif général

Livrer `kb.py stamp-verdict` fonctionnel, dont la preuve de clôture pointe réellement vers
l'exécution du code testé (pas une copie), et dont le scan ne se déclenche jamais sur un bloc
d'exemple — puis faire confirmer cette livraison par un second agent indépendant, à l'aveugle,
avant de la considérer close.

## 3. Objectifs détaillés
- Corriger `tests/verify_kb_index.py` pour qu'il importe et appelle le code de
  `triplet/kb_index.py` plutôt que de dupliquer sa logique.
- Restreindre `PARSE_PREUVE_RE` aux fichiers `VERDICT-*.md` réels, hors blocs de code
  (fences ```` ``` ````) et hors fichiers `MISSION-*.md`.
- Implémenter `validate_preuve_cloture()` et `cmd_stamp_verdict()` dans `kb.py`, conformes au
  schéma `[[preuve_cloture]]` déjà spécifié.
- Capturer une sortie réelle de B1-B7 rejouée sur le code corrigé (pas rétro-fabriquée),
  construire le bloc `[[preuve_cloture]]` à partir de cette capture.
- Exécuter le test de mutation (hash falsifié → `CLOS-NON-PROUVÉ`).
- Faire confirmer l'ensemble par un second agent, sans lui donner le verdict du premier avant
  qu'il ait produit le sien (principe PAMD : « verdict figé avant lecture croisée »).

## 4. Protocole à observer

### Setup
Deux agents distincts, sessions séparées, aucun partage de conclusions avant §5 Partie C :
- **Agent Critique** (implémenteur — ex. opencode/Big Pickle) : reçoit le Prompt A.
- **Agent Contradictoire** (vérificateur indépendant — instance différente, même outil ou
  autre) : reçoit le Prompt B **après** que l'Agent Critique a terminé, mais sans voir son
  rapport de conclusion, seulement le code produit et les fichiers de preuve.

### Métriques à capter
1. `tests/verify_kb_index.py` importe-t-il `triplet.kb_index` (oui/non, preuve : `grep -n
   "^import\|^from" tests/verify_kb_index.py`) ?
2. `PARSE_PREUVE_RE` matche-t-il un bloc d'exemple dans `MISSION-KBIDX-001-*.md` ou dans ce
   fichier (KBIDX-002) après correction ? Doit être : non.
3. Le test de mutation (§5 Partie B, étape 6) échoue-t-il correctement (sort
   `CLOS-NON-PROUVÉ`) ?
4. L'Agent Contradictoire arrive-t-il indépendamment à la même conclusion que l'Agent Critique,
   sans avoir vu son rapport ?

## 5. Procédure / Étapes

### Partie A — Correction du défaut bloquant (préalable, non négociable)
1. Lire `tests/verify_kb_index.py` en entier.
2. Si le script duplique la logique de `build_indexes()` : le réécrire pour importer
   `triplet.kb_index` et appeler directement ses fonctions. Zéro logique dupliquée.
3. Si le script importe déjà correctement : documenter cette confirmation avec la commande
   `grep` exacte et sa sortie — ne pas supposer, vérifier.
4. Rejouer B1-B7 (protocole KBIDX-001) sur le script corrigé. Si un écart apparaît par rapport
   aux résultats précédents (parce que la copie divergeait subtilement de l'original), le
   documenter — c'est un résultat valide, pas un échec de mission.

### Partie B — Correction du défaut mineur + implémentation stamp-verdict
1. Restreindre `PARSE_PREUVE_RE` : ne scanner que les fichiers nommés `VERDICT-*.md`, exclure
   tout contenu situé entre deux lignes ```` ``` ```` (blocs de code).
2. Vérifier explicitement que ce nouveau regex ne matche ni `MISSION-KBIDX-001-*.md`, ni
   `MISSION-KBIDX-002-*.md` (ce fichier), ni le plan d'implémentation d'origine — tous trois
   contiennent un bloc `[[preuve_cloture]]` d'exemple.
3. Ajouter à `kb.py` : `PARSE_PREUVE_RE` corrigé, `validate_preuve_cloture()`,
   `cmd_stamp_verdict()`, dispatcher CLI `stamp-verdict` — logique déjà détaillée dans le plan
   d'implémentation reçu (schéma `[[preuve_cloture]]`, recalcul des deux hash, comparaison,
   VALIDÉ/REJET).
4. Rejouer B1-B7 sur `triplet/kb_index.py`, capturer la sortie brute dans
   `tests/output-b1b7-kbidx002.txt` (pas de sortie déjà existante réutilisée — capture neuve).
5. Construire le bloc `[[preuve_cloture]]` dans `VERDICT-KBIDX-001bis.md` à partir de cette
   capture réelle : `cible_hash` = sha256 du `kb_index.py` réellement testé, `sortie_hash` =
   sha256 du fichier de sortie neuf.
6. Exécuter `kb.py stamp-verdict VERDICT-KBIDX-001bis.md` — doit sortir `CLOS`.
7. **Test de mutation** : modifier manuellement un caractère du hash déclaré, réexécuter — doit
   sortir `CLOS-NON-PROUVÉ`. Documenter la commande et la sortie exacte. Sans ce test réussi, la
   mission n'est pas terminée.
8. Remettre le hash correct après le test (ne pas laisser le fichier dans un état muté).

### Partie C — Revue croisée aveugle (Agent Contradictoire)
1. L'Agent Contradictoire reçoit le Prompt B (§6), le code produit, et les fichiers de preuve —
   **pas** le rapport de conclusion de l'Agent Critique.
2. Il rejoue indépendamment : le `grep` d'import, le test de non-matching sur les fichiers
   d'exemple, et le test de mutation (étape B7 ci-dessus, avec son propre hash falsifié,
   différent de celui utilisé par l'Agent Critique).
3. Il produit son propre verdict, sans connaître celui de l'Agent Critique.
4. Les deux verdicts sont comparés **après coup**, par Andrei. Un désaccord n'est pas un échec
   de mission — c'est un signal diagnostic à documenter, pas à moyenner.

## 6. Prompts à transmettre

### Prompt A — Agent Critique (implémenteur)

```
Tu es l'Agent Critique sur la mission KBIDX-002. Tu ne vois aucun verdict antérieur autre que
les fichiers listés ci-dessous — n'invente pas de contexte au-delà de ce qui est fourni.

Fichiers à lire d'abord, en entier : tests/verify_kb_index.py, triplet/kb_index.py, kb.py,
VERDICT-KBIDX-001bis.md, mission-KBIDX-001-journal.md.

Tâche, dans l'ordre, sans sauter d'étape :
1. Détermine si tests/verify_kb_index.py importe triplet.kb_index ou duplique sa logique.
   Preuve : commande grep exacte + sortie. Si duplication confirmée, corrige-le pour importer
   le code réel. Zéro logique dupliquée dans le fichier final.
2. Rejoue B1-B7 sur le script corrigé. Documente tout écart par rapport aux résultats
   précédemment rapportés.
3. Corrige PARSE_PREUVE_RE pour ne scanner que les fichiers VERDICT-*.md, hors blocs de code
   (```...```). Vérifie explicitement qu'il ne matche PAS MISSION-KBIDX-001-*.md ni
   MISSION-KBIDX-002-*.md.
4. Implémente validate_preuve_cloture() et cmd_stamp_verdict() dans kb.py selon le schéma
   [[preuve_cloture]] (cible_fichier, cible_hash, commande, sortie_fichier, sortie_hash,
   horodatage) — recalcul des deux hash, comparaison, retour VALIDÉ/REJET.
5. Rejoue B1-B7 sur triplet/kb_index.py, capture la sortie brute dans un fichier neuf (pas de
   réutilisation d'une sortie déjà existante).
6. Construis le bloc [[preuve_cloture]] dans VERDICT-KBIDX-001bis.md à partir de cette capture
   réelle.
7. Exécute kb.py stamp-verdict — doit sortir CLOS.
8. Test de mutation obligatoire : falsifie un caractère du hash déclaré, réexécute — doit sortir
   CLOS-NON-PROUVÉ. Documente commande + sortie. Remets le hash correct ensuite.

Interdictions : ne conclus jamais qu'un point est "acceptable" sans le corriger s'il est
corrigeable. Ne réutilise aucune sortie déjà capturée dans une session précédente — toute preuve
doit être une capture neuve de cette session.

Livrable : mission-KBIDX-002-journal.md — log factuel, une entrée par étape, commandes et
sorties brutes incluses, y compris les écarts trouvés.
```

### Prompt B — Agent Contradictoire (vérificateur indépendant)

```
Tu es l'Agent Contradictoire sur la mission KBIDX-002. Tu n'as PAS accès au rapport de
conclusion de l'Agent Critique — seulement au code qu'il a produit et aux fichiers de preuve.
Ton rôle n'est pas de refaire son travail, c'est de le contredire si tu trouves une raison de le
faire. Un accord silencieux n'a aucune valeur diagnostique ici.

Fichiers à lire d'abord, en entier, indépendamment : tests/verify_kb_index.py (version après
correction), triplet/kb_index.py, kb.py (version après ajout stamp-verdict),
VERDICT-KBIDX-001bis.md (version après ajout du bloc [[preuve_cloture]]).

Tâche, sans regarder mission-KBIDX-002-journal.md avant d'avoir terminé :
1. Confirme ou infirme, par ta propre commande grep, que tests/verify_kb_index.py importe
   triplet.kb_index et ne duplique aucune logique.
2. Confirme ou infirme, par ton propre test, que PARSE_PREUVE_RE ne matche ni
   MISSION-KBIDX-001-*.md ni MISSION-KBIDX-002-*.md ni aucun bloc de code d'exemple.
3. Recalcule toi-même cible_hash et sortie_hash à partir des fichiers réels sur disque —
   comparaison directe avec les valeurs déclarées dans [[preuve_cloture]]. Ne fais pas confiance
   aux hash déclarés.
4. Exécute ton propre test de mutation : falsifie un caractère (différent de celui utilisé par
   l'Agent Critique) du hash déclaré, réexécute kb.py stamp-verdict, vérifie que
   CLOS-NON-PROUVÉ sort bien. Remets le hash correct après.
5. Produis ton verdict — CONCORDANT ou DIVERGENT avec ce que tu peux déduire du code — avant de
   lire le journal de l'Agent Critique. Puis compare et documente tout écart entre les deux.

Livrable : verdict-contradictoire-KBIDX-002.md — ton verdict indépendant en premier, la
comparaison avec le journal de l'Agent Critique en second, tout désaccord explicité sans le
minimiser.
```

## 7. Critères de succès
- [ ] `tests/verify_kb_index.py` importe le code réel — confirmé par grep, pas par affirmation
- [ ] `PARSE_PREUVE_RE` corrigé, testé négativement sur les 2 fichiers MISSION-*.md existants
- [ ] `validate_preuve_cloture()` et `cmd_stamp_verdict()` implémentés et fonctionnels
- [ ] Sortie B1-B7 capturée neuve, pas réutilisée d'une session antérieure
- [ ] `kb.py stamp-verdict` sort CLOS sur la preuve réelle
- [ ] Test de mutation réussi (CLOS-NON-PROUVÉ sur hash falsifié), exécuté indépendamment par
      les deux agents avec des mutations différentes
- [ ] Agent Contradictoire a produit son verdict avant de lire celui de l'Agent Critique
- [ ] Tout désaccord entre les deux agents documenté, jamais moyenné ou masqué

## 8. Interdictions
- Ne pas reporter les deux défauts identifiés à une « v2 » — ils sont corrigés dans cette
  mission
- Ne pas laisser l'Agent Contradictoire voir le rapport de l'Agent Critique avant d'avoir
  produit son propre verdict
- Ne pas réutiliser une sortie B1-B7 déjà capturée dans KBIDX-001 comme preuve de KBIDX-002 —
  la capture doit être neuve
- Ne pas committer dans le hub KBM avant verdict final d'Andrei
- Ne pas résoudre un désaccord entre les deux agents par vote ou moyenne — le documenter et le
  remonter

## 9. Placeholders réutilisables
[CHECKLIST_LOCAL] : voir §7
[DECISION_CRITIQUE] : tout désaccord Critique/Contradictoire remonte à Andrei, jamais tranché
  par un agent seul
[KBM_ENTRY] : aucune avant verdict final
[LOG_ENTRY] : une entrée par étape des Parties A, B, C — horodatée, commande + sortie brute

## 10. Format attendu
Rapports de mission :
- `mission-KBIDX-002-journal.md` (Agent Critique — log factuel complet, Parties A et B)
- `verdict-contradictoire-KBIDX-002.md` (Agent Contradictoire — verdict indépendant + comparaison)
Livrables de code :
- `kb.py` mis à jour (stamp-verdict, validate_preuve_cloture, PARSE_PREUVE_RE corrigé)
- `tests/verify_kb_index.py` corrigé (import réel, zéro duplication)
- `VERDICT-KBIDX-001bis.md` avec bloc `[[preuve_cloture]]` réel
- `tests/output-b1b7-kbidx002.txt` — sortie brute capturée
