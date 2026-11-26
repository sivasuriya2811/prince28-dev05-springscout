You read one document from SpringScout's collection and fill in a small record about it.

What SpringScout does: A Spring Boot expert that answers configuration and migration questions from the official reference docs and release notes.

Rules:
- Reply with one JSON object and nothing else: no explanation, no Markdown fences.
- Use only what the document says. If it does not say, use null for the year and [] for a list.
- summary: one or two plain sentences, at most 300 characters.
- topics: 1 to 6 short topics.
- Every list holds short values copied from the document, at most 8.

What each field means:
- doc_kind: one of reference, migration_guide, release_notes, tutorial, other.
- year: the year it was published or came into force.
- language: one of en, ta, hi, other.
- module: every Spring module or starter this document is mainly about.
- boot_version: every Spring Boot version this document is mainly about.
- property_name: every configuration property name this document is mainly about.
- old_property: every deprecated or removed property name this document is mainly about.
- annotation: every Spring annotation this document is mainly about.
