# CTAGS-KB — laboratoire d'évaluation

Ce dépôt documente une exploration indépendante de la valeur d'Universal Ctags
sur un corpus KBM (TOML TI-360 et Markdown), ainsi que le cadre PAMD/KBIDX qui
permet de vérifier ce type de résultat.

## Cadrage

Le projet adopte un cadrage **laboratoire d'idées, en propre**. L'expérience
KBIDX-001 à 003 constitue un cas de référence reproductible : elle montre une
valeur marginale mais réelle de ctags sur un point précis, sans prétendre qu'une
décision d'intégration définitive a déjà été prise pour l'usage réel d'Andrei.
Le protocole PAMD/KBIDX est donc présenté comme une méthode réutilisable pour
d'autres questions, et non comme la validation figée d'un produit à déployer.

## Contenu

- `tools/` : indexation et génération des tags ;
- `tests/` : vérification de l'index ;
- `corpus/all/` : corpus TOML canonique de l'expérience ;
- `missions/kbidx/` : traces chronologiques des trois cycles de vérification ;
- `docs/` : contexte, protocole et verdict général ;
- `classification-nettoyage.md` : décision de sélection depuis le brouillon.

Les sorties générées et les outils de veille/publication KBM ne sont pas inclus.
