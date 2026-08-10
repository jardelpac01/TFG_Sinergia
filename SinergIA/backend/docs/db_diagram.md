# Current database diagram

This diagram reflects the current schema implemented in the project's SQLModel classes and Alembic migrations

```mermaid
erDiagram
    USERS {
        int id PK
        varchar username UK "150"
        varchar email UK "254"
        varchar password_hash "255"
        varchar role "20"
        varchar author_id FK "255"
        datetime created_at
    }

    USER_LOGS {
        int id PK
        int user_id FK
        varchar action "100"
        varchar target_entity "100"
        json details
        varchar ip_address "45"
        datetime created_at
    }

    AUTHORS {
        string id PK
        string display_name
        string orcid
        int h_index
        int works_count
        int cited_by_count
        json counts_by_year
        json raw_data
        string last_known_institution_id FK
        datetime updated_at
    }

    INSTITUTIONS {
        string id PK
        string name
        string country_code "2"
        string ror
        string type
        float geo_lat
        float geo_lon
        string city
        string homepage_url
        json aliases
        int works_count
        int cited_by_count
        json raw_data
        datetime updated_at
    }

    SOURCES {
        string id PK
        string display_name
        string issn
        string publisher
        string type
        string country_code "2"
        bool is_oa
        json raw_data
        datetime updated_at
    }

    WORKS {
        string id PK
        string title
        string abstract
        int publication_year
        date publication_date
        string language "10"
        string doi
        int cited_by_count
        bool is_oa
        string oa_status
        string oa_license
        bool is_retracted
        string type
        string source_id FK
        json raw_data
        datetime updated_at
    }

    TOPICS {
        string id PK
        string display_name
        string subfield
        string field
        string domain
        json raw_data
    }

    CONCEPTS {
        string id PK
        string display_name
        int level
        string wikidata
        string description
        json raw_data
    }

    AUTHOR_WORKS {
        string author_id PK, FK
        string work_id PK, FK
        string author_position
        bool is_corresponding
        string raw_affiliation
    }

    AUTHOR_WORK_AFFILIATIONS {
        string author_id PK, FK
        string work_id PK, FK
        string institution_id PK, FK
        string raw_affiliation
    }

    WORK_TOPICS {
        string work_id PK, FK
        string topic_id PK, FK
        float score
        bool is_primary
    }

    AUTHOR_TOPICS {
        string author_id PK, FK
        string topic_id PK, FK
        float score
    }

    WORK_CONCEPTS {
        string work_id PK, FK
        string concept_id PK, FK
        float score
    }

    AUTHOR_CONCEPTS {
        string author_id PK, FK
        string concept_id PK, FK
        float score
    }

    WORK_REFERENCES {
        string work_id PK, FK
        string referenced_work_id PK, FK
    }

    AUTHOR_YEARLY_METRICS {
        string author_id PK, FK
        int year PK
        int works_count
        int cited_by_count
        int oa_works_count
    }

    USERS ||--o| AUTHORS : "author_id"
    USERS ||--o{ USER_LOGS : "user_id"

    AUTHORS ||--o| INSTITUTIONS : "last_known_institution_id"
    WORKS }o--|| SOURCES : "source_id"

    AUTHORS ||--o{ AUTHOR_WORKS : "author_id"
    WORKS ||--o{ AUTHOR_WORKS : "work_id"

    AUTHORS ||--o{ AUTHOR_WORK_AFFILIATIONS : "author_id"
    WORKS ||--o{ AUTHOR_WORK_AFFILIATIONS : "work_id"
    INSTITUTIONS ||--o{ AUTHOR_WORK_AFFILIATIONS : "institution_id"

    WORKS ||--o{ WORK_TOPICS : "work_id"
    TOPICS ||--o{ WORK_TOPICS : "topic_id"

    AUTHORS ||--o{ AUTHOR_TOPICS : "author_id"
    TOPICS ||--o{ AUTHOR_TOPICS : "topic_id"

    WORKS ||--o{ WORK_CONCEPTS : "work_id"
    CONCEPTS ||--o{ WORK_CONCEPTS : "concept_id"

    AUTHORS ||--o{ AUTHOR_CONCEPTS : "author_id"
    CONCEPTS ||--o{ AUTHOR_CONCEPTS : "concept_id"

    WORKS ||--o{ WORK_REFERENCES : "work_id"
    WORKS ||--o{ WORK_REFERENCES : "referenced_work_id"

    AUTHORS ||--o{ AUTHOR_YEARLY_METRICS : "author_id"
```

## What this schema covers

- `authors` and `works` provide the core of the researcher API: authors, publications, coauthors, affiliations, and topics.
- `institutions`, `sources`, `topics`, and `concepts` add context for navigation and analysis.
- `user_logs` and `users` support basic user management and traceability.
- `raw_data` in several tables preserves the original OpenAlex payload for future expansion without losing the relational structure.

## Applied length limits

- `users.username`: max 150 characters.
- `users.email`: max 254 characters, unique.
- `users.password_hash`: max 255 characters.
- `users.role`: max 20 characters.
- `user_logs.action` / `user_logs.target_entity`: max 100 characters.
- `user_logs.ip_address`: max 45 characters.

## Notes for the thesis

This structure is enough for a first functional prototype for searching and exploring researchers, while remaining flexible enough to incorporate more OpenAlex data in future iterations, such as citation networks, more detailed affiliations, or additional time-based metrics.
