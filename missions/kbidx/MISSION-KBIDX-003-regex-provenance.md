# MISSION — KBIDX-003 — Correction PREUVE_BLOCK_RE (indentation) + clarification provenance

## 0. Métadonnées
Mission ID : KBIDX-003
Date de création : 2026-08-20
Auteur / Agent : Andrei (commanditaire) — Agent Critique (OpenCode) + Agent Contradictoire
(Codex ou instance distincte) requis, même protocole d'étanchéité que KBIDX-002
Projet : Index triples KBM — couche preuve de clôture (suite KBIDX-002)
Statut : ACTIF
Source de vérité : repo de test local, hors KBM

## 1. Contexte

La revue croisée KBIDX-002 a fonctionné exactement comme prévu (Agent Contradictoire produit
son verdict avant de lire le journal de l'Agent Critique) et a détecté une divergence réelle,
confirmée empiriquement par Andrei en exécutant `kb.py stamp-verdict` directement sur le
contenu fourni :

- **Cause technique confirmée** : `PREUVE_BLOCK_RE` n'accepte aucune indentation en début de
  ligne dans le bloc `[[preuve_cloture]]`. La ligne `cible_hash` de `VERDICT-KBIDX-001bis.md`
  est indentée de 6 espaces — le regex arrête sa capture à la première ligne non conforme,
  ne récupère que `cible_fichier`, et `validate_preuve_cloture()` retourne
  `champs manquants` pour les 5 autres champs. Confirmé par mutation contrôlée (retrait de
  l'indentation seule → l'erreur change de nature, passe à `fichier cible introuvable`).
- **Point non résolu, distinct** : le journal `mission-KBIDX-002-journal.md` (Étapes 7-8)
  rapporte une sortie `[PREUVE] ✓ VALIDÉ` puis `cible_hash diverge : déclaré=..., réel=...`
  — non reproductible avec le fichier et le code tels que livrés. Deux hypothèses, non
  départagées : (a) le fichier a été modifié après l'exécution réelle de l'Agent Critique,
  (b) le journal décrit une exécution qui n'a pas eu lieu sous cette forme. Pas de conclusion
  prématurée — l'écart doit être expliqué avec preuve, pas supposé.

## 2. Objectif général

Corriger `PREUVE_BLOCK_RE` pour tolérer l'indentation sans devenir permissif au point de
réintroduire le faux-positif déjà corrigé en KBIDX-002 (blocs d'exemple dans la documentation)
— et obtenir une explication vérifiable de l'écart entre le journal KBIDX-002 et le
comportement réel du code sur le fichier réel.

## 3. Objectifs détaillés
- Corriger `PREUVE_BLOCK_RE` pour accepter un préfixe d'espaces/tabulations en début de chaque
  ligne de champ, sans changer sa portée (toujours limité aux fichiers `VERDICT-*.md`, toujours
  hors blocs de code).
- Rejouer le test négatif déjà établi en KBIDX-002 (aucun faux positif sur
  `MISSION-KBIDX-001-*.md`, `MISSION-KBIDX-002-*.md`, ce fichier) — la correction ne doit rien
  casser de ce qui marchait.
- Rejouer B1-B7 + `stamp-verdict` (CLOS attendu) + test de mutation (CLOS-NON-PROUVÉ attendu)
  sur `VERDICT-KBIDX-001bis.md` **tel qu'il existe actuellement**, avec le regex corrigé.
- Obtenir de l'Agent Critique (OpenCode) une réponse vérifiable aux 3 questions du prompt de
  clarification (§6) — pas une reformulation verbale.
- Faire confirmer l'ensemble par un second agent, à l'aveugle, comme en KBIDX-002.

## 4. Protocole à observer

### Setup
Même dispositif qu'en KBIDX-002 : deux agents, sessions séparées, Agent Contradictoire sans
accès au rapport de l'Agent Critique avant d'avoir produit son propre verdict. L'Agent
Contradictoire ne doit pas nécessairement être Codex à nouveau — instance distincte de l'Agent
Critique suffit, mais si possible garder Codex pour continuité de la trace déjà établie.

### Métriques à capter
1. Le regex corrigé tolère-t-il l'indentation réelle observée (6 espaces) ?
2. Le regex corrigé continue-t-il de rejeter les 3 fichiers de non-régression déjà testés en
   KBIDX-002 ?
3. `stamp-verdict` sur `VERDICT-KBIDX-001bis.md` réel (fichier non modifié depuis KBIDX-002)
   sort-il `CLOS` avec le regex corrigé ?
4. La réponse d'OpenCode au prompt de clarification (§6) est-elle vérifiable (diff, hash,
   horodatage de fichier), ou reste-t-elle une affirmation non prouvée ?
5. L'écart B4 (19 vs 20 tokens numériques) est-il expliqué avec une commande et une sortie
   comparables directement, pas juste réaffirmé ?

## 5. Procédure / Étapes

### Partie A — Correction du regex
1. Modifier `PREUVE_BLOCK_RE` pour tolérer un préfixe `[ \t]*` avant chaque nom de champ
   répété, exemple de piste :
   `r'\[\[preuve_cloture\]\]\s*\n((?:[ \t]*[a-zA-Z_]+\s*=\s*.*\n)*)'`
   — vérifier que ce changement n'affaiblit pas la détection de fin de bloc (une ligne vide ou
   un texte hors-champ doit toujours arrêter la capture).
2. Rejouer le test négatif (aucun faux positif sur les 3 fichiers de documentation identifiés
   en KBIDX-002, plus ce fichier KBIDX-003 lui-même qui contient aussi un extrait de regex en
   exemple).
3. Documenter la commande et la sortie exacte pour chaque test négatif — pas de résumé
   "toujours OK" sans preuve individuelle.

### Partie B — Rejeu sur le fichier réel
1. Exécuter `kb.py stamp-verdict VERDICT-KBIDX-001bis.md --dry-run` avec le regex corrigé, sur
   le fichier **tel qu'il existe actuellement sur disque** (pas une copie reconstruite,
   pas une version antérieure).
2. Si le résultat est `CLOS` : capturer la sortie brute complète.
3. Si le résultat n'est toujours pas `CLOS` (par exemple parce que `cible_hash` ne correspond
   plus au fichier réel `triplet/kb_index.py` actuel) : documenter la raison exacte rapportée
   par le prédicat, sans la contourner.
4. Test de mutation, comme en KBIDX-002 : falsifier un caractère du hash, vérifier
   `CLOS-NON-PROUVÉ` avec la raison `cible_hash diverge` cette fois (et non plus
   `champs manquants`, puisque le regex est corrigé). Documenter. Restaurer ensuite.

### Partie C — Clarification de provenance (Agent Critique)
1. Transmettre à l'Agent Critique le prompt de clarification (§6), tel quel.
2. Exiger une réponse avec preuve technique (diff, hash de fichier à un instant donné,
   horodatage de modification du fichier `VERDICT-KBIDX-001bis.md`) — pas une explication
   narrative seule.
3. Si aucune preuve n'est disponible (par exemple parce que l'environnement d'exécution a été
   remis à zéro entre KBIDX-002 et maintenant) : le déclarer explicitement comme
   NON-DÉTERMINABLE plutôt que de forcer une explication. C'est un résultat valide.

### Partie D — Revue croisée aveugle (identique au protocole KBIDX-002)
1. L'Agent Contradictoire vérifie indépendamment Parties A et B (regex, non-régression, rejeu
   réel, mutation) sans voir le rapport de l'Agent Critique.
2. Il évalue aussi la qualité de la réponse de clarification (Partie C) : preuve reproductible
   ou affirmation non vérifiable ?
3. Verdict indépendant avant lecture croisée, comparaison après.

## 6. Prompt de clarification à transmettre à l'Agent Critique (Partie C)

```
Le test indépendant de Codex, puis une exécution directe par Andrei du kb.py stamp-verdict sur
le contenu exact de VERDICT-KBIDX-001bis.md tel que livré, produisent tous les deux
"champs manquants" (pas "cible_hash diverge") — parce que la ligne cible_hash est indentée
de 6 espaces, ce que PREUVE_BLOCK_RE ne tolère pas.

Ton journal (Étapes 7-8) rapporte une sortie "[PREUVE] ✓ VALIDÉ" puis "cible_hash diverge :
déclaré=..., réel=..." — non reproductible avec ce fichier.

Question directe, à répondre avec preuve, pas avec une explication générale :
1. Le fichier VERDICT-KBIDX-001bis.md a-t-il été modifié (ré-indenté) après ton étape 7,
   par toi ou par un outil externe (éditeur, formatage automatique, export) ? Si oui, montre
   le diff ou le hash du fichier tel qu'il existait au moment de l'étape 7.
2. Si le fichier n'a pas changé depuis l'étape 7 : peux-tu réexécuter exactement
   python3 tools/kb.py stamp-verdict VERDICT-KBIDX-001bis.md --dry-run maintenant et coller
   la sortie brute telle quelle, sans la reformuler ?
3. Vérifie aussi B4 : ton journal rapporte 20 tokens numériques, celui de KBIDX-001bis en
   rapportait 19. Les deux comptes n'ont pas encore été confrontés directement — recompte et
   montre la commande utilisée.

Pas de reformulation de ce qui s'est passé sans la commande et la sortie brute derrière.
```

## 7. Critères de succès
- [ ] `PREUVE_BLOCK_RE` tolère l'indentation réelle observée, sans régression sur les tests
      négatifs déjà établis
- [ ] `stamp-verdict` rejoué sur le fichier réel actuel, résultat documenté avec sortie brute
- [ ] Réponse de l'Agent Critique au prompt §6 obtenue, avec preuve technique ou déclaration
      explicite de NON-DÉTERMINABLE
- [ ] Écart B4 (19 vs 20) expliqué avec commande et sortie comparables directement
- [ ] Agent Contradictoire a produit son verdict avant lecture du rapport de l'Agent Critique
- [ ] Tout désaccord résiduel documenté, jamais moyenné

## 8. Interdictions
- Ne pas accepter une explication narrative de l'écart de provenance sans preuve technique
- Ne pas assouplir `PREUVE_BLOCK_RE` au point de réintroduire un faux positif sur un bloc
  d'exemple en documentation
- Ne pas modifier `VERDICT-KBIDX-001bis.md` pour "faire passer" le test sans que la correction
  de fond (regex) soit la cause du passage
- Ne pas conclure à une fabrication délibérée si l'hypothèse "fichier modifié entre-temps" n'a
  pas été explicitement écartée par preuve

## 9. Placeholders réutilisables
[CHECKLIST_LOCAL] : voir §7
[DECISION_CRITIQUE] : verdict NON-DÉTERMINABLE sur la provenance remonte à Andrei tel quel,
  jamais requalifié en conclusion positive ou négative par un agent
[KBM_ENTRY] : aucune avant verdict final
[LOG_ENTRY] : une entrée par étape des Parties A-D, horodatée, commande + sortie brute

## 10. Format attendu
Rapports de mission :
- `mission-KBIDX-003-journal.md` (Agent Critique)
- `verdict-contradictoire-KBIDX-003.md` (Agent Contradictoire)
Livrables de code :
- `kb.py` avec `PREUVE_BLOCK_RE` corrigé
- `VERDICT-KBIDX-001bis.md` avec `KB-STATUS` final reflétant le résultat réel du rejeu
