---
title: Curation and Ingestion
description: Knowledge extraction, cleaning, normalization, deduplication, provenance tracking, and curation best practices
tags: [knowledge-base, curation, ingestion, deduplication, provenance, metadata]
---

# Curation and Ingestion

## Knowledge Sources

| Source Type | Examples                                   |
| ----------- | ------------------------------------------ |
| Internal    | Databases, documents, wikis, Slack, emails |
| External    | Public data, APIs, third-party sources     |
| Tribal      | SME interviews, recorded conversations     |

## Extraction Methods

- **Automated**: scraping, API ingestion, file parsing
- **Manual**: expert input, annotation, validation

## Cleaning and Normalization

1. Remove duplicates
2. Standardize formats
3. Fix inconsistencies
4. Enrich with metadata

For documents: chunk intelligently at semantic boundaries.
For entities: extract entities, relationships, properties.

## Provenance Tracking

Every knowledge entry needs:

- Source URL or reference
- Last updated timestamp
- Author/contributor
- Confidence score (if applicable)

## Curation Best Practices

| Practice               | Description                                     |
| ---------------------- | ----------------------------------------------- |
| Single source of truth | One canonical answer per question               |
| Deduplication          | Merge similar knowledge entries                 |
| Conflict resolution    | When sources disagree, establish priority rules |
| Metadata richness      | More metadata = better filtering and search     |

## Validation Checklist

- Knowledge extracted and structured
- Quality metrics above threshold (accuracy >95%)
- Provenance tracked for all entries
- Sample queries return relevant results
