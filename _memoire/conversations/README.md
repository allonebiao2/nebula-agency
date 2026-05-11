# Conversations — journal des sessions

> Ce dossier garde une trace des sessions de travail avec Claude (ou autre IA / co-pilote).
> But : retrouver rapidement **ce qui a été décidé et produit** dans une session passée.

---

## Quand créer un log ?

Crée un fichier ici dès qu'une session :
- a structuré le repo / la mémoire,
- a livré ou avancé sur un client,
- a posé une décision importante,
- a produit du code / des prompts à conserver.

**Pas besoin** de logger une session "vite fait" (genre : "corrige une faute dans la vitrine X").

## Nommage des fichiers

```
YYYY-MM-DD-sujet-court-kebab-case.md
```

Exemples :
- `2026-05-11-claude-code-setup.md`
- `2026-05-14-livraison-wecs.md`
- `2026-06-02-debug-n8n-sofia.md`

## Structure d'un log

Toujours partir de `template-session.md` et remplir :

1. **Contexte** — pourquoi la session a eu lieu
2. **Ce qui a été fait** — actions concrètes, dans l'ordre
3. **Décisions** — choix structurants pris pendant la session
4. **Livrables** — fichiers / commits / déploiements produits
5. **À faire ensuite** — prochaines étapes naturelles
6. **À retenir** — apprentissages, à ventiler ensuite dans `_memoire/lecons.md` ou `_memoire/apprentissages/`

## Lien avec les autres mémoires

- **Décisions structurantes** → après la session, dupliquer la décision dans `_memoire/decisions.md`
- **Leçons généralisables** → dupliquer dans `_memoire/lecons.md`
- **Apprentissage technique** → dupliquer dans le bon fichier de `_memoire/apprentissages/`

Le log de session = trace brute. Les autres fichiers de mémoire = trace **distillée**.
