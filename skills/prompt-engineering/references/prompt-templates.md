---
title: Prompt Templates
description: Template architecture with variable rendering, conditional blocks, modular composition, inheritance, validation, caching, and multi-turn conversation templates
tags:
  [
    templates,
    composition,
    modular,
    conditional,
    validation,
    caching,
    conversation,
  ]
---

## Basic Template Structure

```python
class PromptTemplate:
    def __init__(self, template_string, variables=None):
        self.template = template_string
        self.variables = variables or []

    def render(self, **kwargs):
        missing = set(self.variables) - set(kwargs.keys())
        if missing:
            raise ValueError(f"Missing required variables: {missing}")
        return self.template.format(**kwargs)

template = PromptTemplate(
    template_string="Translate {text} from {source_lang} to {target_lang}",
    variables=['text', 'source_lang', 'target_lang']
)

prompt = template.render(
    text="Hello world",
    source_lang="English",
    target_lang="Spanish"
)
```

## Conditional Templates

Handle optional sections with if-blocks and loops:

```python
class ConditionalTemplate(PromptTemplate):
    def render(self, **kwargs):
        import re
        result = self.template

        if_pattern = r'\{\{#if (\w+)\}\}(.*?)\{\{/if\}\}'
        def replace_if(match):
            var_name = match.group(1)
            content = match.group(2)
            return content if kwargs.get(var_name) else ''

        result = re.sub(if_pattern, replace_if, result, flags=re.DOTALL)

        each_pattern = r'\{\{#each (\w+)\}\}(.*?)\{\{/each\}\}'
        def replace_each(match):
            var_name = match.group(1)
            content = match.group(2)
            items = kwargs.get(var_name, [])
            return '\n'.join(content.replace('{{this}}', str(item)) for item in items)

        result = re.sub(each_pattern, replace_each, result, flags=re.DOTALL)
        return result.format(**kwargs)
```

## Modular Composition

Register reusable components and compose them for different scenarios:

```python
class ModularTemplate:
    def __init__(self):
        self.components = {}

    def register_component(self, name, template):
        self.components[name] = template

    def render(self, structure, **kwargs):
        parts = []
        for component_name in structure:
            if component_name in self.components:
                parts.append(self.components[component_name].format(**kwargs))
        return '\n\n'.join(parts)

builder = ModularTemplate()
builder.register_component('system', "You are a {role}.")
builder.register_component('context', "Context: {context}")
builder.register_component('instruction', "Task: {task}")
builder.register_component('examples', "Examples:\n{examples}")
builder.register_component('input', "Input: {input}")
builder.register_component('format', "Output format: {format}")

basic_prompt = builder.render(
    ['system', 'instruction', 'input'],
    role='helpful assistant',
    task='Summarize the text',
    input='...'
)
```

## Common Template Patterns

### Classification

```python
CLASSIFICATION_TEMPLATE = """
Classify the following {content_type} into one of these categories: {categories}

{content_type}: {input}

Category:"""
```

### Extraction

```python
EXTRACTION_TEMPLATE = """
Extract structured information from the {content_type}.

Required fields:
{field_definitions}

{content_type}: {input}

Extracted information (JSON):"""
```

### Generation

```python
GENERATION_TEMPLATE = """
Generate {output_type} based on the following {input_type}.

Requirements:
{requirements}

{input_type}: {input}

{output_type}:"""
```

## Template Inheritance

```python
class TemplateRegistry:
    def __init__(self):
        self.templates = {}

    def register(self, name, template, parent=None):
        if parent and parent in self.templates:
            base = self.templates[parent]
            template = {**base, **template}
        self.templates[name] = template

registry = TemplateRegistry()

registry.register('base_analysis', {
    'system': 'You are an expert analyst.',
    'format': 'Provide analysis in structured format.'
})

registry.register('sentiment_analysis', {
    'instruction': 'Analyze sentiment',
    'format': 'Provide sentiment score from -1 to 1.'
}, parent='base_analysis')
```

## Variable Validation

Validate types, ranges, and allowed values before rendering:

```python
class ValidatedTemplate:
    def __init__(self, template, schema):
        self.template = template
        self.schema = schema

    def validate_vars(self, **kwargs):
        for var_name, var_schema in self.schema.items():
            if var_name in kwargs:
                value = kwargs[var_name]
                if 'type' in var_schema and not isinstance(value, var_schema['type']):
                    raise TypeError(f"{var_name} must be {var_schema['type']}")
                if 'choices' in var_schema and value not in var_schema['choices']:
                    raise ValueError(f"{var_name} must be one of {var_schema['choices']}")

    def render(self, **kwargs):
        self.validate_vars(**kwargs)
        return self.template.format(**kwargs)

template = ValidatedTemplate(
    template="Summarize in {length} words with {tone} tone",
    schema={
        'length': {'type': int, 'min': 10, 'max': 500},
        'tone': {'type': str, 'choices': ['formal', 'casual', 'technical']}
    }
)
```

## Multi-Turn Conversation Templates

```python
class ConversationTemplate:
    def __init__(self, system_prompt):
        self.system_prompt = system_prompt
        self.history = []

    def add_user_message(self, message):
        self.history.append({'role': 'user', 'content': message})

    def add_assistant_message(self, message):
        self.history.append({'role': 'assistant', 'content': message})

    def render_for_api(self):
        messages = [{'role': 'system', 'content': self.system_prompt}]
        messages.extend(self.history)
        return messages
```

## Best Practices

1. **Keep it DRY**: Use templates to avoid repetition
2. **Validate early**: Check variables before rendering
3. **Version templates**: Track changes like code
4. **Test variations**: Ensure templates work with diverse inputs
5. **Provide defaults**: Set sensible default values where appropriate
6. **Cache wisely**: Cache static templates, not dynamic ones
