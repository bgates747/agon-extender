# Replay assistance source reconciliation

No new hardware lease or target operation has started. The preliminary owner
manifest committed as108203bb is superseded and must not be used for admission.
Its source list predates the corrected release observer and the consumer's new
runner. The first complete recheck rejected the consumer run.py/kit mismatch;
this is a preparation stop, not a physical failure or an uncertain test.

1. Original consumer kit expects5770B/49dc84fa; working runner is7929B/a3086b7a
   at the observed checkpoint. MechAgon owns the current edits and final exact
   publication/kit update. Do not revert its source or silently replace hashes.
2. Extender corrected a duplicate release-observer keyword before target use.
   Syntax compilation now covers every owner leaf; AST parsing alone would
   not detect duplicate call keywords.
3. A shell command incorrectly continued to Git after the failed freeze check,
   publishing the earlier preparation manifest. No admission followed. Later
   publication must consume only a successful, complete freeze, with separate
   preflight readiness invalidated before each refresh and no stale ready file.
4. Retain this correction and closed59 evidence. Prepare checked operator gates
   while the consumer finishes its source freeze, then publish a fresh manifest
   revision before normal fresh admission. No hardware retry/replay is involved.
