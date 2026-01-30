---
title: Entity Extraction
description: NER pipeline for entity extraction, entity resolution and deduplication, relationship extraction with dependency parsing, and LLM-based extraction for complex relationships
tags: [ner, entity-extraction, entity-resolution, relationship-extraction, llm]
---

# Entity Extraction & Relationship Building

## Data Sources

- **Structured**: Databases, APIs, CSV files
- **Unstructured**: Documents, web content, text files
- **Semi-structured**: JSON, XML, knowledge bases

## Entity Extraction Pipeline

```python
class EntityExtractionPipeline:
    def __init__(self):
        self.ner_model = load_ner_model()  # spaCy, Hugging Face
        self.entity_linker = EntityLinker()
        self.deduplicator = EntityDeduplicator()

    def process_text(self, text: str) -> List[Entity]:
        # 1. Extract named entities
        entities = self.ner_model.extract(text)

        # 2. Link to existing entities (entity resolution)
        linked_entities = self.entity_linker.link(entities)

        # 3. Deduplicate and resolve conflicts
        resolved_entities = self.deduplicator.resolve(linked_entities)

        return resolved_entities
```

## Relationship Extraction

```python
class RelationshipExtractor:
    def extract_relationships(self, entities: List[Entity],
                            text: str) -> List[Relationship]:
        relationships = []

        # Use dependency parsing or LLM for extraction
        doc = self.nlp(text)
        for sent in doc.sents:
            rels = self.extract_from_sentence(sent, entities)
            relationships.extend(rels)

        # Validate against ontology
        valid_relationships = self.validate_relationships(relationships)
        return valid_relationships
```

## LLM-Based Extraction (Complex Relationships)

```python
def extract_with_llm(text: str) -> List[Relationship]:
    prompt = f"""
    Extract entities and relationships from this text:
    {text}

    Format: (Entity1, Relationship, Entity2, Confidence)
    Only extract factual relationships.
    """

    response = llm.generate(prompt)
    relationships = parse_llm_response(response)
    return relationships
```

## Validation

- Entity extraction accuracy > 85%
- Entity deduplication working
- Relationships validated against ontology
- Confidence scores assigned
