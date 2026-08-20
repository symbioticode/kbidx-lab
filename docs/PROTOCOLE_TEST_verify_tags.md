# PROTOCOLE TEST — verify_tags

**Date:** 2026-08-12
**Type:** PROTOCOLE
**Statut:** ACTIF
**Portée:** Vérification de l'intégrité du fichier `tags` généré par
`kb_tags.py` (corpus KBM TOML). Protocole rejouable, hors KBM
(`/home/andrei/Projects/68_CTAGS-KB`).

---

## Objectif

S'assurer que chaque entrée du fichier `tags` :
1. résout vers un fichier existant du corpus ;
2. pointe vers la **bonne ligne** (la définition de l'`id`) ;
3. est **unique** (ou explicitement une collision d'instance partagée) ;
4. est **trie** (prérequis Vim pour la recherche binaire) ;
5. est **lisible par Vim** (jump-to-tag réel, pas seulement le format).

## Prérequis

- `ctags` 6.2.1 (via `nix-shell -p universal-ctags`) — optionnel, §6 seulement.
- `nvim` ou `vim` présent.
- Corpus de test : `corpus/*/*.toml`.

## Étape 1 — Générer les tags

```bash
cd /home/andrei/Projects/68_CTAGS-KB
rm -f tags-kbtags
for f in corpus/*/*.toml; do python3 kb_tags.py "$f" >> tags-kbtags; done
# Les pseudo-tags (!_TAG_*) doivent rester en tête : trier le corps, puis
# re-préfixer l'en-tête (un tri global déplacerait !_TAG_* après les lettres,
# ASCII '!' < 'A' mais > '0').
awk '!/^!_TAG_/{print}' tags-kbtags > tags-kbtags.body
sort -o tags-kbtags.body tags-kbtags.body
awk '/^!_TAG_/{print}' tags-kbtags > tags-kbtags.head
cat tags-kbtags.head tags-kbtags.body > tags-kbtags
rm -f tags-kbtags.head tags-kbtags.body
```

**Critère d'acceptation** : exit 0, aucune sortie stderr, pseudo-tags en tête.

## Étape 2 — Pseudo-tags et tri

```bash
# 2a. La pseudo-tag de garde doit être en tête
head -1 tags-kbtags | grep -q "^!_TAG_"
# 2b. Le corps doit être trié lexicographiquement (ordre LANG=C).
#     Exclure l'en-tête : sort -c comparerait '!_TAG_...' avec les tags
#     ('!' < 'a' en ASCII), fausse alerte.
awk '!/^!_TAG_/{print}' tags-kbtags | LC_ALL=C sort -c && echo "tri OK"
# 2c. Aucun pseudo-tag égaré dans le corps
awk '!/^!_TAG_/{print}' tags-kbtags | grep -c "^!_TAG_"
```

**Critère d'acceptation** : 2a OK, 2b « tri OK », 2c renvoie 0 (ou rien).

## Étape 3 — Fichiers référencés existants

```bash
# Chaque chemin de tag doit exister. Filtrer l'en-tête par la COLONNE 1
# (les pseudo-tags ont des champs '1'/'2' en col. 2 — un filtre naïf sur la
# ligne les ferait remonter comme fichiers manquants).
awk -F"\t" '$1 !~ /^!_TAG_/ {print $2}' tags-kbtags | sort -u |
  while read -r f; do [ -f "$f" ] || echo "MANQUANT: $f"; done
```

**Critère d'acceptation** : aucune sortie (tous les chemins existent).

## Étape 4 — Correspondance tag → ligne exacte

Pour **tous** les tags (pas un échantillon) :

```bash
# Vérifie que la ligne pointée par le tag contient bien `id = "<tag>"`
python3 - << 'EOF'
import re, sys
ID_LINE_RE = re.compile(r'^id[ \t]*=[ \t]*"([^"]+)"')
bad = 0
with open("tags-kbtags", encoding="utf-8") as f:
    for line in f:
        if line.startswith("!_TAG_"):
            continue
        parts = line.rstrip("\n").split("\t")
        tag, path, lineno = parts[0], parts[1], int(parts[2].rstrip(';"'))
        with open(path, encoding="utf-8") as src:
            target = src.readlines()[lineno - 1]
        m = ID_LINE_RE.match(target)
        if not m or m.group(1) != tag:
            bad += 1
            print(f"DEFAUT: {tag} -> {path}:{lineno} ligne={target.rstrip()}")
print(f"tags vérifiés: {sum(1 for _ in open('tags-kbtags') if not _.startswith('!_TAG_'))}, défauts: {bad}")
sys.exit(1 if bad else 0)
EOF
```

**Critère d'acceptation** : `défauts: 0`, exit 0.

## Étape 5 — Unicité et collisions

```bash
# Tags dupliqués (même nom, chemins différents) = ambiguïté → :tselect
awk -F"\t" '!/^!_TAG_/{print $1}' tags-kbtags | sort | uniq -d
# Collisions attendues : instances partagées entre fichiers (inst-andrei, etc.)
# => vérifier que chaque nom dupliqué EST bien une instance partagée, pas une erreur
```

**Critère d'acceptation** : les seuls noms dupliqués sont des ids d'`instance`
communs à plusieurs sessions (liste blanche), pas des `ext-*`/`dec-*`/`src-*`.

## Étape 6 — Jump-to-tag réel dans Vim (test fonctionnel)

```bash
# 6a. Le tag existe et saute au bon fichier/ligne
nvim --headless -u NONE +'set tags=tags-kbtags' +'tag dec-kbm-010' \
  +'redir! > /tmp/opencode/tagcheck.txt' \
  +'echo line(".") . ": " . getline(".")' +'redir END' +'qa!' 2>&1
cat /tmp/opencode/tagcheck.txt   # attendu: ligne de la table [[decision]]

# 6b. Lookup cross-fichiers
nvim --headless -u NONE +'set tags=tags-kbtags' +'tag src-client-leger-2026-08-10' \
  +'redir! > /tmp/opencode/tagcheck2.txt' \
  +'echo expand("%:t") . ":" . line(".")' +'redir END' +'qa!' 2>&1
cat /tmp/opencode/tagcheck2.txt  # attendu: session-...-client-leger-nixos.toml:<ligne>

# 6c. Absence d'E434 / E426 (pattern introuvable / tag introuvable)
! grep -q "E434\|E426" /tmp/opencode/tagcheck*.txt
```

**Critère d'acceptation** : 6a → ligne `id = "dec-kbm-010"`, 6b → bon fichier,
6c → aucune erreur E434/E426.

## Étape 7 — Régression : rejouer après modification de kb_tags.py

Chaque modification de `kb_tags.py` (format de sortie, kinds, filtres) doit
rejouer les étapes 2-6 intégralement. Aucune modification n'est exemptée.

## Résultat attendu sur le corpus actuel (2026-08-12)

- 105 entités (36 extraction, 22 instance, 21 decision, 11 source,
  8 reunion, 7 question).
- 5 collisions = instances partagées (attendues).
- 54 ids référentiels (`src-*`/`dec-*`/`inst-*`) résolvables.
- Génération < 1 s.
- 0 défaut, 0 E434/E426.

## Limites du protocole

- Valide la **justesse mécanique** (tag → ligne), pas la **justesse
  sémantique** (un `id` dupliqué à tort dans le TOML reste invisible ici —
  relève de kb.py, invariants 1-9).
- Le jump Vim est testé headless ; la vérification du comportement
  interactif (`:tselect` sur collision) reste manuelle.
