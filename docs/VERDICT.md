# CTAGS-KB — Banc de test : valeur de Ctags sur un corpus KBM

**Date:** 2026-08-12
**Type:** REPORT
**Statut:** ACTIF (évaluation)
**Portée:** Test hors KBM — aucune modification du hub KBM.

---

## Question

Universal Ctags apporte-t-il de la valeur sur un corpus KBM (TOML TI-360
+ Markdown) ? Faut-il l'intégrer ?

## Méthode

- Corpus de test copié hors KBM : 10 TOML (`corpus/*/`) + 6 Markdown
  (`markdown/kbm/`) depuis `~/TEMP/kbm-home-real`.
- ctags 6.2.1 (via nix-shell).
- Deux chemins testés : parseur natif TOML/Markdown de ctags, et générateur
  maison `kb_tags.py` (tables TOML → format `tags`).

## Résultats

### 1. Parseur natif ctags

| Format | Parseur | Résultat |
|---|---|---|
| TOML | **désactivé** (bug boucle infinie, retiré en 6.2.0) | activable `--languages=+TOML`, mais 564 tags = **bruit** : tagge les clés (`beta`, `contenu`, `baseline_cycles` dupliqués 7×) au lieu des valeurs utiles (`dec-kbm-010`, etc.) |
| Markdown | actif | fonctionne : chapitres `c` + sections `s` (78 tags sur 6 fichiers) |

### 2. kb_tags.py (générateur maison, tables → tags)

- **105 entités** taggées : 36 extractions, 22 instances, 21 décisions,
  11 sources, 8 réunions, 7 questions.
- **54 ids référentiels** (`src-*`, `dec-*`, `inst-*`) résolvables en un
  lookup direct → navigation **inter-fichiers** fonctionnelle dans Vim.
- Collisions : 5 (instances partagées entre fichiers — normal, résolu par
  `:tselect`).
- Coût : **0,4 s** pour tout le corpus. Zéro dépendance, stdlib seule.

### 3. Pièges découverts (corrigés)

1. Vim cherche les patterns de tags en **nomagic** : `\s` est lu littéralement
   → E434. **Solution : numéros de ligne** dans le fichier tags (format natif).
2. Pattern `id = "x"` collide avec `decision_id = "x"` → ancrage `^id`.
3. `sort -o tags tags` requis avant tout lookup Vim (recherche binaire).

## Valeur apportée

| Critère | ctags | Existant KBM (kbm_catalog.py) |
|---|---|---|
| Naviguer d'une référence à sa définition (cross-file) | ✅ instantané, dans Vim | ❌ grep manuel |
| Granularité | ✅ entité (extraction/décision/source) | nœuds projet/artefact |
| Rapprochement références croisées | ✅ 54 ids direct | graphe 173 nœuds / 409 arêtes |
| Vue sémantique / contexte IA | ❌ tags = indices, pas de sens | ✅ `ai-context.md` + `graph.json` |
| Graphe de relations projet-artefact | ❌ | ✅ |
| Validation structurelle | ❌ | ✅ kb.py (invariants 1-9) |
| Dettes de forme | ❌ | ✅ quality-report |

## Verdict

**Oui, valeur marginale mais réelle — sur un point précis uniquement.**

Ctags **ne remplace rien** de l'existant : il n'apporte ni validation
(kb.py), ni graphe, ni qualité (kbm_catalog.py). Sa seule valeur propre est
la **navigation directe référence → définition dans l'éditeur** (jump to
tag), que le KBM n'a pas.

Recommandation :
- **Intégrer `kb_tags.py`** (déjà corrigé, ~50 lignes, stdlib) comme générateur
  de tags à la volée pour les sessions d'édition Vim/Neovim sur les TOML.
- **Ne pas** remplacer `kbm_catalog.py`/`kb.py` par ctags.
- Parseur TOML natif ctags : **à ignorer** (bruit + désactivé).
- Parseur Markdown : utile pour sauter aux sections d'un gros `.md`, mais
  redondant avec la table des matières MkDocs.

## Artefacts produits

- `kb_tags.py` — générateur tags (stdlib, lignes de définition exactes).
- `tags-kbtags` — tags du corpus de test (105 entités).
- `tags-markdown` — tags Markdown (sections).
- `toml.ctags` — esquisse optlib (abandonnée, groupe imbriqué non gérable).
- `corpus/`, `markdown/` — copie de test (hors KBM).

## Pour aller plus loin

- Hook Vim/Neovim : `autocmd BufWritePost *.toml !kb_tags.py % >> tags`.
- Si le volume explose (> 1000 TOML), passer en JSON (`--output-format=json`)
  ou SQLite ; aujourd'hui 0,4 s pour 10 fichiers, inutile d'optimiser.
