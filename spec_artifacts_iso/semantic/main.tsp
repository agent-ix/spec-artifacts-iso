import "@typespec/json-schema";
import "@agent-ix/semantic-core";

using TypeSpec.JsonSchema;
using AgentIx.Semantic.Core;

/**
 * Semantic data models of the spec-artifacts-iso module (FR-005, ticket
 * agent-ix/spec-artifacts-iso#34).
 *
 * One model per ISO artifact type. Each model is the typed form of the record
 * the archetype's `body_extraction` locators already extract, plus the
 * frontmatter identity, relationships, status, and provenance. The Markdown is
 * the authority and the record is a derived projection (FR-007); the models
 * describe requirement definitions, never execution results.
 *
 * Every field carries a constraint. Where a field is free text the doc comment
 * says `free text:` and why (FR-005-AC-3).
 */
@jsonSchema("https://schemas.agent-ix.org/agent-ix/spec-artifacts-iso/")
namespace AgentIx.SpecArtifactsIso;

// ---------------------------------------------------------------------------
// Scalars
// ---------------------------------------------------------------------------

/** A non-empty string; the base of every prose cell and every name. */
@minLength(1)
scalar NonEmptyText extends string;

/** Functional requirement id (`FR-N`). */
@pattern("^FR-[0-9]+$")
scalar FRId extends string;

/** Non-functional requirement id (`NFR-N`). */
@pattern("^NFR-[0-9]+$")
scalar NFRId extends string;

/** Stakeholder requirement id (`StR-N`); the frontmatter schema pins the same form. */
@pattern("^StR-[0-9]+$")
scalar StRId extends string;

/** User story id (`US-N`). */
@pattern("^US-[0-9]+$")
scalar USId extends string;

/** Integration test id (`IT-N`). */
@pattern("^IT-[0-9]+$")
scalar ITId extends string;

/** Test case id (`TC-N`). */
@pattern("^TC-[0-9]+$")
scalar TCId extends string;

/** Glossary id: a 2..4 letter prefix and a number (`GLO-001`); the frontmatter schema requires only non-empty. */
@pattern("^[A-Z][A-Za-z]{1,3}-[0-9]+$")
scalar GlossaryId extends string;

/** Acceptance-criterion row id: `<FR|NFR id>-AC-N`, the locator `id_pattern`. */
@pattern("^(FR|NFR)-[0-9]+-AC-[0-9]+$")
scalar AcceptanceCriterionId extends string;

/** Constraint row id: `<FR id>-CON-N`, the locator `id_pattern`. */
@pattern("^FR-[0-9]+-CON-[0-9]+$")
scalar ConstraintId extends string;

/** Validation-criterion row id: `<StR id>-VC-N`, the locator `id_pattern`. */
@pattern("^StR-[0-9]+-VC-[0-9]+$")
scalar ValidationCriterionId extends string;

/** Per-step success-criterion token of an integration test: `<IT id>-SC-N` (lint rule `it-success-criteria`). */
@pattern("^IT-[0-9]+-SC-[0-9]+$")
scalar SuccessCriterionId extends string;

/** A test-case reference the split extracts from an annotated verification
 * cell, e.g. `TC-035` out of `Test (TC-035)` — a cell shape no skeleton
 * authors, kept for a caller that still annotates one. */
@pattern("^TC-[0-9]+$")
scalar TestCaseRef extends string;

/**
 * Lifecycle status from frontmatter `status`. The value set is deliberately
 * open: the corpus uses many spellings (`APPROVED`, `IMPLEMENTED`, `DRAFT`,
 * `PROPOSED`, `SUPERSEDED` and minor forms); closing it is a vocabulary
 * decision that needs its own sweep-and-report, not a side effect of this
 * schema.
 */
@pattern("^[A-Za-z][A-Za-z_-]*$")
scalar ArtifactStatus extends string;

/** A relationship verb from the module's `edge_types` registry (FR-004). */
@pattern("^[a-z][a-z0-9_]*$")
scalar EdgeVerb extends string;

/** A relationship target: an `ix://` identity, as the frontmatter schemas require. */
@pattern("^ix://.+$")
scalar IxTarget extends string;

/**
 * Relationship cardinality as authored. Admits these forms:
 * `1:1`, `1:N`, `N:1`, `n:1`, `1`, `0:1`, `1:n`, `many:1`,
 * `1..1`, `0..1`, `1:m`; each side is a number, a letter token, or `*`,
 * optionally a `..` range.
 */
@pattern("^[0-9A-Za-z*]+(\\.\\.[0-9A-Za-z*]+)?(:[0-9A-Za-z*]+(\\.\\.[0-9A-Za-z*]+)?)?$")
scalar Cardinality extends string;

/** SHA-256 over the document bytes, `sha256:<64 hex>` (the FR-073 digest form). */
@pattern("^sha256:[0-9a-f]{64}$")
scalar Sha256Digest extends string;

/** A 1-based document line number. */
@minValue(1)
scalar LineNumber extends int32;

/** A calendar date `YYYY-MM-DD` as the log skeleton writes it. */
@pattern("^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
scalar IsoDate extends string;

/** A relative link target (`./FR-001-x.md`, `functional/index.md`); never a scheme, because index links are local navigation, not graph edges. */
@pattern("^(\\./|\\.\\./)*[^:/][^:]*$")
scalar RelativeHref extends string;

/** An object-type name from frontmatter `object:` (`entity`, `api_endpoint`). */
@pattern("^[a-z][a-z0-9_]*$")
scalar ObjectTypeName extends string;

/** Master-requirements `component_type`, kebab-case as the frontmatter schema pins. */
@pattern("^[a-z][a-z0-9-]*$")
scalar ComponentType extends string;

/** The ISO 25010 quality characteristics the NFR frontmatter schema enumerates. */
enum QualityAttribute {
  functional_suitability,
  performance_efficiency,
  compatibility,
  usability,
  reliability,
  availability,
  security,
  maintainability,
  portability,
  scalability,
  compliance,
  safety,
}

// ---------------------------------------------------------------------------
// Shared models
// ---------------------------------------------------------------------------

/**
 * One level-2 section as a `section` mapping yields it: the byte-exact section
 * content (quire-rs FR-008) and its document lines.
 */
model Section {
  /** free text: authored prose; sentence grammar is the `iso-spec-core` EARS advisory, not a schema. */
  text: string;
  startLine: LineNumber;
  endLine: LineNumber;
}

/** A heading-presence locator's yield: the heading text and its line (master-requirements containers). */
model HeadingRef {
  heading: NonEmptyText;
  line: LineNumber;
}

/** Where the record came from. */
model Provenance {
  /** Corpus-relative path of the document. */
  path: NonEmptyText;
  /** `ix://<org>/<repo>/spec` when the caller supplies it; absent on the `validate_document` surface. */
  sourceIdentity?: SemanticId;
  /** SHA-256 over the document bytes as read. */
  digest: Sha256Digest;
}

/**
 * One frontmatter `relationships[]` entry, sealed to the three keys the record
 * carries. FR-003 admits extra annotation keys on a relationship item (`note`,
 * `models`, `endpoints`); they cannot reach a sealed model, so the FR-007
 * `frontmatter` mapping drops them and lists them as dropped keys — a declared
 * loss, not a silent one.
 */
model Relationship {
  target: IxTarget;
  type: EdgeVerb;
  cardinality?: Cardinality;
}

/**
 * A verification or validation cell split by the `typed-table` mapping. The
 * skeletons author a plain cell — `Test` is `method: Test`, `testRefs: []`,
 * no `annotation`. A cell still carrying parentheses splits into `method`,
 * `annotation` (the text between the first `(` and the last `)` verbatim, so
 * no byte of the authored cell is dropped), and `testRefs` (the `TC-nnn`
 * tokens found in `annotation`). The split keeps parsing that shape for a
 * caller that still authors one, but a criterion binds to its tests by
 * criterion id, not a cell annotation.
 */
model Verification {
  /** free text: on FR/NFR this is the Verification cell, owned by spec-artifacts-process's lint rule (ISO 29148 methods plus its catalog method ids); on StR this is the Validation cell, owned by this module's advisory `vc-validation-method` rule (the four ISO 29148 methods). A schema that closed the vocabulary would reject the corpus it describes. */
  method: NonEmptyText;
  testRefs: TestCaseRef[];
  /** free text: the parenthesized remainder of the cell, verbatim, so the split loses nothing the author wrote. */
  annotation?: string;
}

/** One `## Acceptance Criteria` row (`ID | Criteria | Verification`). */
model AcceptanceCriterion {
  id: AcceptanceCriterionId;
  /** free text: the criterion statement; measurability is judged by review and the EARS advisory. */
  criteria: NonEmptyText;
  verification: Verification;
  /** free text: body of a supplementary `### <criterion id>` subsection, when one exists. */
  detail?: string;
  line: LineNumber;
}

/** One `## Constraints` row (`ID | Constraint | Type | Validation`). */
model Constraint {
  id: ConstraintId;
  /** free text: the constraint statement. */
  constraint: NonEmptyText;
  /** free text: the constraint category; no rule owns the vocabulary. */
  type: NonEmptyText;
  validation: Verification;
  line: LineNumber;
}

/** One `## Validation Criteria` row of a stakeholder requirement (`ID | Criteria | Validation`). */
model ValidationCriterion {
  id: ValidationCriterionId;
  /** free text: the criterion statement. */
  criteria: NonEmptyText;
  validation: Verification;
  line: LineNumber;
}

/** One `## Measurement and Evaluation` row (`Metric | Target | Threshold | Method`). */
model MeasurementRow {
  /** free text: the metric name. */
  metric: NonEmptyText;
  /** free text: a prose quantity with its unit (`600 imports/s`); typing it needs a unit grammar this module does not own. */
  target: NonEmptyText;
  /** free text: a prose quantity, as `target`. */
  threshold: NonEmptyText;
  /** free text: the measurement method in the author's words. */
  method: NonEmptyText;
  line: LineNumber;
}

/** One `IT-XXX-SC-NN` success-criterion token of `## Test Procedure` with the text that follows it on its line. */
model SuccessCriterion {
  id: SuccessCriterionId;
  /** free text: the criterion statement. */
  text: NonEmptyText;
  line: LineNumber;
}

/** The `## Story` section parsed by the `story` locator's regex (As a / I want / So that). */
model Story {
  /** free text: the role clause. */
  asA: NonEmptyText;
  /** free text: the need clause. */
  iWant: NonEmptyText;
  /** free text: the value clause. */
  soThat: NonEmptyText;
  section: Section;
}

/** One `## Terms` row (`Term | Definition`); the term feeds the EARS lexicon (FR-044). */
model GlossaryTerm {
  term: NonEmptyText;
  /** free text: the definition. */
  definition: NonEmptyText;
  line: LineNumber;
}

/** One `* [title](href) - summary` line of an index `## Contents`. */
model IndexEntry {
  title: NonEmptyText;
  href: RelativeHref;
  /** free text: the trailing summary after ` - `, when present. */
  summary?: string;
  line: LineNumber;
}

/** One `* **YYYY-MM-DD** — text` entry of a log `## History`. */
model LogEntry {
  date: IsoDate;
  /** free text: the entry body after the date. */
  text: NonEmptyText;
  line: LineNumber;
}

// ---------------------------------------------------------------------------
// Artifact models (exported)
// ---------------------------------------------------------------------------

/** Functional requirement record (archetype `FR`). */
model FR {
  id: FRId;
  title: NonEmptyText;
  type: "FR";
  object?: ObjectTypeName;
  status?: ArtifactStatus;
  relationships: Relationship[];
  provenance: Provenance;
  description: Section;
  inputs?: Section;
  outputs?: Section;
  behavior?: Section;
  @minItems(1) constraints?: Constraint[];
  @minItems(1) acceptanceCriteria: AcceptanceCriterion[];
  /** Formal clauses from an optional `## Invariants` section (`ocl-clause` mapping); clause text is carried beside the record, never parsed. */
  @minItems(1) invariants?: ClauseRef[];
  dependencies: Section;
}

/** Non-functional requirement record (archetype `NFR`). */
model NFR {
  id: NFRId;
  title: NonEmptyText;
  type: "NFR";
  qualityAttribute?: QualityAttribute;
  object?: ObjectTypeName;
  status?: ArtifactStatus;
  relationships: Relationship[];
  provenance: Provenance;
  statement: Section;
  scope?: Section;
  rationale?: Section;
  @minItems(1) measurement: MeasurementRow[];
  verification: Section;
  /** Present only for a policy NFR; a measurable NFR's criteria are its measurement rows. */
  @minItems(1) acceptanceCriteria?: AcceptanceCriterion[];
  dependencies?: Section;
}

/** Stakeholder requirement record (archetype `StR`). */
model StR {
  id: StRId;
  title: NonEmptyText;
  type: "StR";
  object?: ObjectTypeName;
  status?: ArtifactStatus;
  relationships: Relationship[];
  provenance: Provenance;
  stakeholderNeed: Section;
  rationale: Section;
  @minItems(1) validationCriteria: ValidationCriterion[];
  stakeholders?: Section;
  contextAndAssumptions?: Section;
  stakeholderConstraints?: Section;
  dependencies?: Section;
  priorityAndRisk?: Section;
  notes?: Section;
  traceability?: Section;
}

/** User story record (archetype `US`); every section but the story is contextual and non-binding. */
model US {
  id: USId;
  title: NonEmptyText;
  type: "US";
  object?: ObjectTypeName;
  status?: ArtifactStatus;
  relationships: Relationship[];
  provenance: Provenance;
  story: Story;
  context?: Section;
  /** Illustrative by the US contract: nothing here is binding or verification criteria, so the section stays prose. */
  acceptanceExamples?: Section;
  options?: Section;
  constraints?: Section;
  dependencies?: Section;
  priorityAndRisk?: Section;
  notes?: Section;
  traceability?: Section;
}

/** Integration test record (archetype `IT`): the test's definition, never its run. */
model IT {
  id: ITId;
  title: NonEmptyText;
  type: "IT";
  object?: ObjectTypeName;
  status?: ArtifactStatus;
  relationships: Relationship[];
  provenance: Provenance;
  objective: Section;
  targetIntegration: Section;
  preconditions: Section;
  inputs: Section;
  testProcedure: Section;
  /** One per `IT-XXX-SC-NN` token in the procedure; empty when the author declared none (the lint rule is advisory). */
  successCriteria: SuccessCriterion[];
  expectedResults: Section;
  metadata?: Section;
  dependencies?: Section;
  notes?: Section;
  traceability?: Section;
}

/**
 * Test case record (archetype `TC`). `expectedResults` is the definition of what
 * a passing run shows; execution results (pass/fail, run time, evidence) are
 * not modelled here or anywhere in this module.
 */
model TC {
  id: TCId;
  title: NonEmptyText;
  type: "TC";
  object?: ObjectTypeName;
  status?: ArtifactStatus;
  relationships: Relationship[];
  provenance: Provenance;
  description: Section;
  testProcedure: Section;
  expectedResults: Section;
}

/** Master requirements specification record (archetype `master-requirements`). */
model MasterRequirements {
  type: "master-requirements";
  name: NonEmptyText;
  org: NonEmptyText;
  componentType: ComponentType;
  title?: NonEmptyText;
  /** `null` is authored for components without one; the frontmatter schema admits it. */
  implementationLanguage?: NonEmptyText | null;
  tags?: NonEmptyText[];
  /** Bare module names. */
  dependsOn?: NonEmptyText[];
  standardsAlignment?: NonEmptyText[];
  securityCritical?: boolean;
  status?: ArtifactStatus;
  relationships: Relationship[];
  provenance: Provenance;
  purpose: Section;
  scope: HeadingRef;
  systemOverview: HeadingRef;
  requirementsArchitecture: HeadingRef;
  references: Section;
}

/** Directory index record (archetype `index`, OKF reserved file). */
model Index {
  type: "index";
  title?: NonEmptyText;
  /** free text: the frontmatter description. */
  description?: string;
  okfVersion?: NonEmptyText;
  provenance: Provenance;
  entries: IndexEntry[];
}

/** Update log record (archetype `log`, OKF reserved file). */
model Log {
  type: "log";
  title?: NonEmptyText;
  /** free text: the frontmatter description. */
  description?: string;
  provenance: Provenance;
  @minItems(1) history: LogEntry[];
}

/** Ubiquitous-language glossary record (archetype `Glossary`, FR-044). */
model Glossary {
  id: GlossaryId;
  title: NonEmptyText;
  type: "Glossary";
  scope?: NonEmptyText;
  /** free text: the frontmatter description. */
  description?: string;
  status?: ArtifactStatus;
  relationships: Relationship[];
  provenance: Provenance;
  @minItems(1) terms: GlossaryTerm[];
}
