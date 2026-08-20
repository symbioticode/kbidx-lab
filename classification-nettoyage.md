# Classification de nettoyage — 69_CTAGS-KB

Date : 2026-08-20

Le brouillon original est conservé intact. Le nouveau dépôt sera construit par
copie sélective dans un dossier frère ; aucun fichier n'est déplacé ni supprimé
du brouillon.

## A — Vues générées, régénérables, non versionnées

- `index-run1/` et `index-fixed/` : sorties JSON générées par les exécutions de
  l'indexeur.
- `triplet/by_id.json`, `triplet/by_relation.json`, `triplet/by_term.json` :
  sorties générées ; les fichiers source et le code `kb_index.py` sont conservés.
- `tags-kbtags`, `tags-line`, `tags-markdown`, `tags-toml`, `tags-toml-all` :
  sorties de Universal Ctags.
- `__pycache__/` sous `staging/`, `tests/`, `tools/` et `triplet/` : bytecode
  Python régénérable.

Ces éléments sont couverts par `.gitignore` et ne sont pas copiés dans le dépôt
propre.

## B — Corpus dupliqué

Vérification effectuée par `diff -qr` :

- `corpus/client-leger-nixos/` : 1 fichier partagé identique avec `corpus/all` ;
  les 9 autres fichiers sont uniquement dans `all`.
- `corpus/home/` : 1 fichier partagé identique avec `corpus/all` ; les 9 autres
  fichiers sont uniquement dans `all`.
- `corpus/kbm/` : 8 fichiers partagés identiques avec `corpus/all` ; les 2
  autres fichiers sont uniquement dans `all`.

Les trois différences sont donc des sous-ensembles exacts. Seul
`corpus/all/` devient la source canonique.

## C — Hors périmètre

- `staging/` : chantier de staging d'un autre flux, notamment CT-2026-012/013.
- `tools/veille2kbm.py` et `tools/youtube_kbm_publish.py` : outils de veille/
  publication KBM, sans lien avec l'expérience ctags/index KB.
- `tools/kb_registry_scan.py` : outil de registre/veille KBM, hors cœur ctags.
- `markdown/kbm/` : documentation et missions du projet KBM général, distinctes
  de l'étude ctags.

Ces éléments restent dans le brouillon et dans le snapshot, mais ne sont pas
copiés dans le dépôt propre.

## D — Livrable réel du chantier

À conserver dans le dépôt propre :

- `gestion-acces-connaissance.md`
- `PROTOCOLE_TEST_verify_tags.md`
- `RAPPORT_SITUATION_2026-08-12.md`
- `VERDICT.md`
- `tools/kb.py`, `tools/kb_tags.py`
- `triplet/kb_index.py`, déplacé logiquement sous `tools/kb_index.py`
- `tests/verify_kb_index.py` et `tests/b1b7-output-kbidx002.txt`
- tous les fichiers KBIDX : missions, journaux, `VERDICT-KBIDX-*` et
  `verdict-contradictoire-KBIDX-*`.

## Non classé — décision

- `session-ses_fe7d.md` : trace d'une session d'exploration d'agent, contenant
  surtout le contexte de découverte et des instructions de skill. Elle n'est
  pas une preuve du protocole ni un livrable ctags ; conservation dans
  l'archive du brouillon, exclusion du dépôt propre.
- `TI-360-note-de-presentation.docx` : note générale de présentation de TI-360,
  utile comme contexte institutionnel mais hors question de recherche ctags.
  Conservation dans l'archive du brouillon, exclusion du dépôt propre.

## Cadrage retenu

Le nouveau dépôt adopte le cadrage B — laboratoire d'idées en propre. La
question ctags a été explorée et vérifiée, mais aucune décision d'intégration
définitive n'a été validée pour l'usage réel d'Andrei. Le dépôt présente donc
PAMD/KBIDX comme un cadre déterministe et réutilisable, avec ctags comme cas de
référence, plutôt que comme un outil déjà officiellement adopté.

## Anomalies

- Le comptage demandé du snapshot donne 97 entrées tar contre 76 fichiers réels,
  car `tar tzf` compte aussi les répertoires. L'archive a été confirmée par
  Andrei et aucun fichier original n'a été modifié avant cette confirmation.
- `gh` est installé mais non authentifié : les jetons des comptes détectés sont
  invalides. La création GitHub devra donc être faite manuellement après
  authentification.
