# CT-2026-014 — Documenter un contexte distribué de collaboration IA

**Statut :** PROPOSED
**Langue du CT :** français
**Langue du dépôt public :** anglais
**Cible :** dépôt public `project-feedback-loop`

## Objectif

Documenter comment des humains, des agents locaux et une IA orchestratrice
peuvent partager un contexte frais et vérifiable à travers des projets, des
Change Tickets et des articles de connaissance. La boucle de feedback est le
résultat de la composition de micro-procédures utiles, pas l'objectif initial.

## Origine opérationnelle

Le travail part d'une dérive récurrente entre les fichiers locaux, les articles
de connaissance, les déclarations d'état, les sessions IA et les vues de
projets. Les problèmes pratiques sont la mise à jour manuelle du contexte, le
travail non tagué, l'absence de déclarations d'état, la répétition des
explications aux agents et l'absence d'un dashboard léger pour une équipe de
deux ou trois personnes.

La documentation publique abstrait le setup privé sous les noms **MyCollabIA**
(autorité de collaboration et de portefeuille) et **MyKnowledgeBase**
(Obsidian, MkDocs, Markdown/TOML ou une autre couche de connaissance).

## Fondements conceptuels

- Edwin Hutchins, *Cognition in the Wild* : cognition distribuée entre les
  personnes, les artefacts et les procédures.
- Nonaka et Takeuchi, *The Knowledge-Creating Company* : conversion et
  circulation de la connaissance organisationnelle.
- W3C PROV : provenance reliant les sources, activités et entités produites.

Ces références fournissent un cadre conceptuel ; elles ne constituent pas une
validation académique de l'implémentation.

## Scénarios

Le même modèle d'unité suivie couvrira les projets, les Change Tickets et les
articles de connaissance. Chaque unité possède un identifiant, un état, une
priorité, un responsable, des sources, une dernière observation, une prochaine
action et un niveau de confiance.

## Livrable

Un dépôt public entièrement en anglais contenant une documentation explicative,
des schémas texte, des fixtures anonymisées, un petit kit Python, des exemples
de planificateurs, des tests et une voie de contribution Windows avec PowerShell
et Windows Task Scheduler.

## Gate

Ce CT concerne uniquement le cadrage documentaire. La création et la
publication du dépôt suivent l'enregistrement du CT.
