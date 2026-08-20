# Rapport de nettoyage — 69_CTAGS-KB

Date : 2026-08-20

## Snapshot

Archive confirmée par Andrei :
`/home/andrei/backup-69_CTAGS-KB-brouillon-20260820.tar.gz`.
Le comptage brut `tar tzf` était de 97 entrées contre 76 fichiers réels, l'écart
venant des répertoires comptés par tar. Aucun fichier du brouillon n'a été
supprimé ni remplacé.

## Tri effectué

- A : sorties générées et `__pycache__` exclues.
- B : `client-leger-nixos`, `home` et `kbm` comparés par `diff -qr` ; aucun
  contenu partagé ne diverge de `corpus/all`. Seul `corpus/all` a été copié.
- C : staging, outils veille/publication KBM et `markdown/kbm` exclus.
- D : outils ctags/index, tests, documentation sélectionnée et KBIDX-001 à 003
  copiés.
- `session-ses_fe7d.md` et `TI-360-note-de-presentation.docx` conservés dans
  l'archive mais exclus du dépôt propre, car contextuels et hors livrable ctags.

La classification détaillée est dans `classification-nettoyage.md`.

## Nouveau dépôt local

`/home/andrei/Projects/69_CTAGS-KB-propre`

Cadrage choisi : **B — laboratoire d'idées, en propre**. La décision
d'intégration réelle n'étant pas encore validée, le dépôt présente PAMD/KBIDX
comme méthode réutilisable et KBIDX comme cas de référence.

Premier commit : `d43d873 Initialiser le laboratoire CTAGS-KB`.
Vérification : 28 fichiers suivis ; aucun fichier A ou C présent dans
`git ls-files`.

## GitHub

`gh` est installé, mais l'authentification est invalide pour les comptes
détectés. Aucun dépôt distant ni URL n'a donc été créé.

Après `gh auth login`, commandes exactes :

```bash
cd /home/andrei/Projects/69_CTAGS-KB-propre
gh repo create 69_CTAGS-KB --public --source=. --remote=origin --push
```

Anomalies : l'écart de comptage tar décrit ci-dessus et l'absence
d'authentification GitHub ; aucun diff non vide ni doublon inattendu dans les
sous-corpus.
