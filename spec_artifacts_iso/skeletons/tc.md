---
id: TC-001
title: "Reject artifact with mismatched digest"
type: TC
relationships:
  - target: "ix://agent-ix/example/FR-001"
    type: "verifies"
---
<!-- TC authoring skeleton (spec-artifacts-iso). ISO/IEC/IEEE 29119 test case.
     Fill every section with substantive content. Contract (manifest
     body_extraction asserts):
     - REQUIRED (level 2): Description, Test Procedure, Expected Results.
     - Keep it minimal — a test case is a single concrete check; richer
       orchestration belongs in an IT artifact.
     - Keep headings unique per level; nest ≤2 levels below the H1 title. -->
# [TC-001] Reject artifact with mismatched digest

## Description

Verify that importing an artifact whose declared digest differs from the digest
computed over its bytes is rejected and leaves the artifact store unchanged.

## Test Procedure

With the import service running and the store empty, submit an artifact whose
declared SHA-256 digest does not match its bytes to the import endpoint, then
query the store for the submitted artifact's identifier.

## Expected Results

The request is rejected with a digest-mismatch error reporting both the declared
and computed digests, and the store contains no artifact for the submitted
identifier.
