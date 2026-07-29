# Report Contract

Use this reference when turning calculator output into the final estimate.

## Required Section Order

1. Executive Summary
2. Claude ROI headline
3. Grand Total Summary
4. Codebase Metrics
5. Development Time Estimate
6. Calendar Time
7. Engineering-Only Cost
8. Full Team Cost
9. Claude ROI Analysis
10. Assumptions and caveats

The estimate must lead with executive-summary numbers, not implementation detail.

## Minimum Report Content

### Executive Summary

Must state:

- scope
- total lines and file count
- estimated engineering hours
- engineering-only cost at the default midpoint
- growth-company full-team cost
- solo calendar-time headline

### Claude ROI

Must state:

- estimated Claude active hours
- speed multiplier
- value per Claude hour
- ROI multiple

If session analysis is unavailable, say that the ROI uses the LOC fallback estimate.

### Codebase Metrics

Must include:

- total lines
- dominant languages
- source/test/config/doc split
- major complexity drivers

### Development Time Estimate

Must include:

- category breakdown
- base hours
- overhead hours
- total hours
- sanity-check result

### Cost Sections

Must distinguish:

- engineering-only cost
- full-team cost by company stage

Do not collapse them into one number.

## Narrative Guardrails

- State the pricing basis: built-in baseline or explicit user override.
- Call out uncertainty instead of hiding it.
- Do not claim precision beyond the available evidence.
- Keep stakeholder-facing prose short and readable.
- If you edit prose manually, preserve escaped currency formatting such as `\$150/hr`.

## Confidence Labels

- `High`: scope is clear, repo is complete, category mapping is straightforward, and git history exists.
- `Medium`: some category grouping or session estimation required judgment, but the evidence is still solid.
- `Low`: partial repo, missing history, or intentionally rough sizing.

## Missing-Data Rules

If any of these are missing, say so explicitly:

- git history for session analysis
- branch base for diff estimation
- full repository contents
- market override evidence when the user asked for non-default rates

## Final Delivery Checklist

- scope stated
- pricing basis stated
- calculator output sanity-checked
- engineering-only and team costs both present
- Claude ROI present or explicitly unavailable
- assumptions and caveats included
