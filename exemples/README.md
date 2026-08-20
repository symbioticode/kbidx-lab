# Exemples d'utilisation

Ces exemples sont dérivés de deux usages réels, mais restent des fixtures
minimales et autonomes : ils ne copient pas les dépôts privés ni le corpus de
travail complet.

## 1. YOUTUBE-KB : état d'un fichier traité par une IA

Les entrées de `21_YOUTUBE_KB/entries/` portent notamment un identifiant vidéo,
un `review_status` et parfois un `quality_status`. Dans un flux de traitement,
ces champs répondent à la question : « cette fiche est-elle encore à revoir ou
peut-elle être considérée comme suffisamment examinée ? »

Voir :

- `youtube-kb.toml` : représentation structurée pour l'agent ;
- `youtube-kb.tags` : index de type ctags produit par `tools/kb_tags.py` ;
- `vue-humaine.html` : rendu lisible dans un navigateur ;
- `vue-agent.toml` et `vue-agent.regex` : accès ciblé aux états et aux relations.

## 2. MyDashboard : état d'un projet

Le dashboard privé agrège les projets et leur couche `kb_status` : nombre de
fichiers marqués et liste des statuts rencontrés. La vue humaine montre une
carte de projet ; la vue machine expose les mêmes valeurs sous une forme stable,
interrogeable par un agent ou un générateur de dashboard.

Les valeurs sont un exemple reproductible inspiré de la structure de
`02_MYDASHBOARD/dashboard.yaml`, pas une copie de données privées en temps réel.

## Rejouer

Depuis la racine du dépôt :

```bash
python3 tools/kb_tags.py exemples/youtube-kb.toml > exemples/youtube-kb.tags
```

Le fichier `.tags` est volontairement commité ici comme résultat pédagogique ;
les tags produits dans un vrai projet restent des artefacts régénérables et sont
couverts par `.gitignore`.
