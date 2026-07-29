# Term Schema Reference

## Full Term Example

```yaml
  # ─── Cart ────────────────────────────────────
  - name: Cart
    definition: A temporary collection of items a user intends to purchase.
    aliases:
      - Shopping Cart
      - Basket
    code_name: cart
    ui_label: "Shopping Bag"
    status: active
    tags:
      - user-facing
      - core
    related:
      - contains: Cart Item
      - leads_to: Checkout Session
        when: "Cart contains at least one item"
    notes: >
      In the UK market, "Basket" is used in the UI instead of "Shopping Bag".
```

## Field Reference

| Field | Required | Type | Description |
| --- | --- | --- | --- |
| `name` | Yes | string | The canonical term name. Title case. |
| `definition` | Yes | string | Plain-language definition anyone can understand. 1-2 sentences. |
| `aliases` | No | list | Other names people use for this term. |
| `code_name` | No | string | What developers call it in backend code. snake_case or camelCase. |
| `ui_label` | No | string | What users see in the frontend. Exact UI text. |
| `status` | No | string | `active` (default), `deprecated`, or `proposed`. |
| `tags` | No | list | Freeform tags for filtering. Common: `user-facing`, `internal`, `core`. |
| `related` | No | list | Typed relationships to other terms (see Relationships). |
| `notes` | No | string | Additional context, exceptions, regional differences. |

## Relationship Types

| Type | Meaning | Auto-inferred inverse |
| --- | --- | --- |
| `contains` | Parent owns children | `part_of` |
| `references` | Uses but doesn't own | `referenced_by` |
| `leads_to` | Flow to a different entity | `follows` |
| `transitions_to` | Same entity, new state | `transitions_from` |
| `replaces` | Deprecated term superseded | `replaced_by` |

### Relationship Design Principles

- **Define once, infer the inverse.** If Cart `contains` Cart Item, the inverse (Cart Item `part_of` Cart) is auto-generated. Only store forward relationships in YAML.
- **No `parent` field.** Parentage is derived from `contains` relationships.
- **No `synonym_of`.** Use `aliases` instead — one mechanism for "same thing, different name."
- **Optional `when` conditions** capture business rules on relationships:

```yaml
    related:
      - leads_to: Checkout Session
        when: "Cart contains at least one item"
      - leads_to: Saved for Later
        when: "User is signed in"
```

- **`transitions_to` vs `leads_to`:** Flow between different entities (`leads_to`) vs state change of the same entity (`transitions_to`):

```yaml
  - name: Order
    definition: A confirmed purchase with payment received.
    related:
      - contains: Order Line
      - transitions_to: Shipped Order    # same entity, new state
      - leads_to: Invoice                # different entity
```

## Separator Convention

Terms are separated by a comment line for legibility:

```yaml
  # ─── Term Name ──────────────────────────────
```

Generate these automatically when adding terms. The dashes should pad to roughly column 50.

## Config File Structure

```yaml
# glossary.config.yml
project: ProjectName
description: Ubiquitous language for the project.
default_language: en

contexts:
  - file: core.glossary.yml
    scope: "*"
  - file: checkout.glossary.yml
    scope: "src/checkout/**"
  - file: fulfillment.glossary.yml
    scope: "src/fulfillment/**"
```

## Context File Structure

```yaml
# checkout.glossary.yml
context:
  name: Checkout
  description: The process of completing a purchase, from cart review to payment confirmation.

terms:

  # ─── Term 1 ─────────────────────────────────
  - name: Term 1
    definition: ...

  # ─── Term 2 ─────────────────────────────────
  - name: Term 2
    definition: ...
```

## Mermaid Diagram Generation

When regenerating `relationships.md`, produce:

1. **One diagram per context** showing relationships between terms within that context
2. **One cross-context diagram** showing terms that appear in multiple contexts, linked with dashed lines

Template:

```markdown
# Term Relationships

## [Context Name]

​```mermaid
graph TD
    TermA -->|relationship_type| TermB
    TermB -->|relationship_type| TermC
​```

## Cross-Context Relationships

​```mermaid
graph LR
    subgraph Context1
        Term_C1[Term]
    end
    subgraph Context2
        Term_C2[Term]
    end
    Term_C1 -.->|"same entity, different context"| Term_C2
​```
```

Use `-->` for directional relationships, `-.->` for cross-context links. Node IDs should be the term name with spaces replaced by underscores.
