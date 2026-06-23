---
id: GLO-001
title: "Order Management Glossary"
type: Glossary
scope: order-management
---
<!-- Glossary authoring skeleton (spec-artifacts-iso, FR-044). A project's
     Ubiquitous-Language vocabulary. Contract (manifest body_extraction
     asserts, validated by `quire validate`):
     - REQUIRED (level 2): Terms — a table with headers EXACTLY
       Term | Definition, with >= 1 data row.
     - The `Term` column is harvested by quire-rs and fed to the EARS
       object-aware vague-response check (FR-042/043) as accepted concrete
       terms, so a requirement that says "the system shall provide a
       <glossary term>" is not flagged as vague.
     - Define terms the project uses in a SPECIFIC way (ISO/IEC/IEEE 29148
       glossary intent); common industry terms ship in the module lexicons
       and need not be repeated here.
     - Keep headings unique per level. -->
# [GLO-001] Order Management Glossary

## Terms

| Term | Definition |
|------|------------|
| Place | Convert a draft order into a binding purchase request. |
| Capture | Confirm payment for a placed order at the authorised amount. |
| Fulfilment | The pick, pack, and ship work that completes a paid order. |
| Cancellation window | The period during which a placed order may still be cancelled without compensation steps. |
