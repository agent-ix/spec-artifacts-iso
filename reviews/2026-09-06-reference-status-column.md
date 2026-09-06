# Reference status-column schema amendment

Parent: `6686f112f2c38602c9d39c88e8134a945c34bbd6`. Scope is quire-rs#409's
optional `DocumentReference.status_column`, with a nonblank string check and
no default or required key. The engine owns the global-vocabulary dependency.
No emitted model schemas, skeletons or declaration pins changed.

Spec-first and banked controls preceded the implementation. The parent fails
the three positive overrides and exact-delta control (four failures, nine
negative cases passing); the amended schema passes all 13 new cases. The 51
existing schema/manifest-loading controls also pass. Removing the exact added
property must recover the parent's raw schema SHA-256
`52bddd1c14e0df06e95322db45734925990a4472e6b4c980a5c14f00480bb874`.

The crossover with process parent `ccc2bea19de857d9adb765b7c64065ae5efbb387`
and its one-field candidate confirms: old schema plus parent passes; old schema
plus candidate fails only for unexpected status_column; new schema accepts both.
This is schema qualification, not native engine or full ecosystem qualification.
The older `codex/reference-status-columns` work was inspected but not merged:
its parent predates the current semantic schema work and its minLength-only
constraint would admit whitespace. Current canonical-main additions are retained.

Existing validation-stack pins remain ISO `a6b1c70be8c22e9f7cb432e4410b7a3a280d0217`
and process `61a20e010d5e758f52864ad3152ccdb304a39d27`. They are historical
inputs, not these new candidates. The coordinator owns reviewed exact pin moves.
