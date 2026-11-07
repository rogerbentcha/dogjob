# Dogjob : diagramme entité-association (MVP)

> Source : `SPEC.md` § 5 « Modèle de données (MVP) » et ADR-003 (offre = candidature).
> Notation en pattes de corbeau (crow's foot).

```mermaid
erDiagram
    ENTREPRISE ||--o{ CANDIDATURE : "reçoit"
    CANDIDATURE ||--o{ HISTORIQUE_STATUT : "trace"

    ENTREPRISE {
        int id PK
        varchar nom UK "insensible à la casse et aux espaces"
        varchar site_web "nullable"
        text notes "nullable"
    }

    CANDIDATURE {
        int id PK
        int entreprise_id FK "NOT NULL"
        varchar titre
        varchar url "nullable"
        text description "nullable"
        statut statut "défaut À postuler"
        timestamptz postule_le "nullable, renseigné au passage en Postulé"
        int nb_relances "défaut 0, max 3"
        timestamptz derniere_relance_le "nullable"
        timestamptz cree_le
        timestamptz modifie_le
    }

    HISTORIQUE_STATUT {
        int id PK
        int candidature_id FK "NOT NULL"
        statut de_statut "nullable à la création"
        statut vers_statut
        timestamptz change_le
        source source "manuel | auto"
    }
```

## Cardinalités

| Relation | Lecture | Notation |
|---|---|---|
| Entreprise → Candidature | Une entreprise a **zéro ou plusieurs** candidatures ; une candidature appartient à **exactement une** entreprise. | `\|\|--o{` |
| Candidature → HistoriqueStatut | Une candidature a **zéro ou plusieurs** changements de statut ; un changement concerne **exactement une** candidature. | `\|\|--o{` |

## Contraintes

- `ENTREPRISE.nom` : unique après normalisation (casse et espaces superflus), par exemple un index unique sur `lower(trim(nom))`.
- `CANDIDATURE.entreprise_id` : `ON DELETE RESTRICT`, car la suppression d'une entreprise ayant des candidatures est refusée (409, F1).
- `HISTORIQUE_STATUT.candidature_id` : `ON DELETE CASCADE` si la suppression d'une candidature est définitive (question ouverte, F7).

## Énumérations

- `statut` : `À postuler`, `Postulé`, `Entretien`, `Offre reçue`, `Refusé`, `Sans suite`.
- `source` : `manuel`, `auto`.
