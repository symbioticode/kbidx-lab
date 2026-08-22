# CTAGS-KB — rendre l'état de la connaissance lisible

Ce dépôt explore une question très concrète : **comment une connaissance vit-elle,
et peut-on mieux capturer ses états ?**

Il s'inscrit dans un ensemble plus large de modules autour de la gestion de la
connaissance — DUO, PCCD et d'autres à venir. Chaque module traite un aspect
indépendant ; une fois réunis, ils doivent permettre d'expliquer une théorie plus
générale de la connaissance fiable, traçable et exploitable.

## Le problème de départ

KBM est une base de connaissance double dans sa structure :

- une couche **Markdown**, lisible par l'utilisateur ;
- une couche **TOML**, extraite et structurée par `kb.py`, qui donne aux agents IA
  accès au sens et aux relations entre les éléments.

L'utilisateur consulte surtout le Markdown. Les agents IA, eux, naviguent dans le
graphe produit à partir du TOML. Mais ils ne disposent pas naturellement de
l'équivalent de ce que les développeurs ont avec Universal Ctags : une vue rapide
des éléments nommés, de leur type, de leur emplacement et de leurs relations.

Le TOML introduit en outre des relations qui peuvent former des boucles. Une
simple liste de tags ne suffit donc pas toujours. C'est la raison de
`kb_tags.py` : produire une indexation adaptée à KBM, puis mesurer ce qu'elle
apporte réellement.

La question n'est pas seulement : « le projet est-il tagué ? » Elle est :

> **Quel bénéfice concret cette indexation apporte-t-elle à une IA ou à un
> utilisateur qui doit comprendre, retrouver ou suivre l'état d'une connaissance ?**

## Pourquoi les états comptent

Dans le workflow réel, le statut d'un fichier ou d'un projet doit être exploitable
par des outils et visible dans un tableau de bord :

- dans un tableau de bord privé de type **MyDashboard**, pour suivre le statut
  des projets ;
- dans **YOUTUBE-KB**, pour savoir où en sont les fichiers traités par des IA ;
- dans le **change management**, où chaque CT doit déclarer un `KB-STATUS` afin
  de distinguer ce qui est en suspens, en cours d'exécution ou échoué.

Le statut doit voyager avec le document, être lisible sans interprétation manuelle
et rester vérifiable. L'indexation et les tags sont utiles seulement dans la
mesure où ils rendent ces états plus faciles à trouver, relier et contrôler.

## Ce que contient ce laboratoire

Ce dépôt est le laboratoire indépendant qui a servi à évaluer cette hypothèse sur
un corpus KBM composé de TOML TI-360 et de Markdown.

- `tools/kb.py` : extraction, validation et gestion des statuts de connaissance ;
- `tools/kb_tags.py` : génération de tags adaptés au corpus KBM ;
- `tools/kb_index.py` : construction de l'index des relations ;
- `tests/` : vérifications reproductibles ;
- `missions/kbidx/` : trois cycles KBIDX documentant les tests, les mutations,
  les désaccords et leur résolution — ou leur caractère indéterminable ;
- `corpus/all/` : corpus TOML canonique utilisé par l'expérience ;
- `docs/` : contexte, protocole et verdict de l'exploration.
- `exemples/` : un même type d'information présenté pour l'œil humain et pour
  une consommation machine, à partir de cas YOUTUBE-KB et MyDashboard.

Le résultat de l'exploration est volontairement mesuré : Universal Ctags et
l'indexation associée apportent une valeur marginale mais réelle sur certains
accès structurés. Ce dépôt ne prétend pas qu'une intégration définitive est déjà
validée dans tous les usages de KBM.

## Comment lire le résultat

Le projet ne cherche pas à remplacer la lecture humaine du Markdown ni le graphe
TOML. Il cherche à ajouter une vue de repérage et d'état : une manière de
répondre plus vite à « qu'est-ce qui existe ? », « où est-ce défini ? », « à quoi
est-ce relié ? » et « dans quel état se trouve ce fichier ou ce projet ? ».

La valeur pour une IA doit être jugée sur ces gains d'accès et de vérifiabilité,
pas sur le simple nombre de tags produits.

Les exemples de `exemples/` montrent cette séparation : le HTML rend un état
compréhensible en un coup d'œil ; le TOML et les motifs regex rendent les mêmes
champs repérables et exploitables par un agent ou un script.

## Périmètre et suite

Le dépôt reste un **laboratoire d'idées en propre**. Les outils de publication ou
de veille KBM, notamment `kb_registry_scan.py` et `youtube_kbm_publish.py`,
appartiennent à d'autres flux et ne sont pas inclus ici comme livrables.

PAMD est le cadre de vérification utilisé pour rendre les résultats
reproductibles et contradictoirement examinés. Il mérite probablement son propre
dépôt lorsque la manière de faire travailler Git et PAMD en bonne intelligence
sera suffisamment comprise et stabilisée.

Le prochain enjeu n'est donc pas de figer ce module, mais de déterminer comment
ses vues — tags, relations et statuts — s'assemblent avec les autres modules pour
décrire le cycle de vie complet de la connaissance.

## Projet feedback loop

Le sous-projet [`project-feedback-loop/`](project-feedback-loop/) généralise ce
problème au suivi de projets, de Change Tickets et d'articles KB. Il fournit un
petit kit Python sans agent IA obligatoire : déclaration TOML, observation de
signaux, provenance et projections texte, JSON et HTML. Il constitue un exemple
réutilisable de la manière dont les états peuvent circuler entre fichiers,
connaissance, scripts et contexte de collaboration.

Pour l'exécuter :

```text
python3 project-feedback-loop/kit/refresh.py project-feedback-loop/examples/minimal
```
