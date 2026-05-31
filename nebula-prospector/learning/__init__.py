"""V5 — Auto-amélioration de NOVA.

Chaque dimanche soir, NOVA relit ses interactions de la semaine, identifie
ce qui marche et ce qui ne marche pas, et :
1. Génère un document d'apprentissages hebdo (timestamped)
2. Propose une mise à jour de sa mission si pertinent
3. Crée des skills auto-déduits des patterns gagnants
4. Notifie Mongazi du résumé hebdo

C'est le mécanisme qui rend NOVA progressivement plus intelligente,
inspiré de l'`update_mission` / `create_document` NanoCorp.
"""
