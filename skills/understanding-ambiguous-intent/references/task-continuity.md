# Task continuity

Use this reference when continuing substantial work, incorporating corrections,
or handing an active task to another agent. Use the host's existing task or
checkpoint mechanism when available. This reference supplies no background
worker, storage service, cross-session access or new authorization.

## Preserve the smallest useful state

Keep a concise record of:

- The requested outcome and exact target.
- Current constraints, exclusions and applicable authorization boundaries.
- Material corrections and which previous decisions they replace.
- Completed work with supporting artifact or observed result references.
- Remaining work, unresolved choices and the next useful action.
- Whether the task is active, blocked, completed, cancelled or replaced.

Keep uncertainty explicit. A saved summary and a prior assistant's completion
claim are starting points for verification, not proof that an external action
occurred. Never store hidden reasoning transcripts. Keep private task state
outside public source repositories.

## Interpret the next turn

| Incoming turn | Update |
|---|---|
| A progress question during active work | Answer briefly, then continue the authorized remaining work. |
| A correction to one detail | Replace that detail and retain unaffected requirements. |
| A compatible additional requirement | Add it within actual scope and permissions; adjust the remaining work. |
| An explicit cancellation | Mark the task cancelled and stop its pending actions. Retain evidence of effects already performed. |
| A clearly incompatible replacement | Use the new goal; do not continue obsolete actions. |
| "Continue" after cancellation | Resolve what should continue if no active task can be established. |
| Advice requested after completion | Give advice; earlier execution authorization does not make this new question an instruction to implement. |

Do not interpret a short progress question as cancellation, or a detailed
question as a permanent preference. If tools or task ownership have changed,
report the specific limitation and make only claims supported by current state.

## Example handoff

The following is synthetic. It is optional task data, not a mandatory output
format and not an authorization record.

```json
{
  "task_id": "workshop-copy",
  "status": "active",
  "goal": "Prepare the workshop announcement",
  "target": "draft announcement",
  "constraints": ["Two sentences", "No sending", "Preserve Room 3"],
  "corrections": ["Use 11:00 instead of 10:00"],
  "verified_progress": [],
  "remaining": ["Write the revised draft", "Check time and room"],
  "next_action": "Produce the two-sentence draft",
  "uncertainties": []
}
```

Verify material state when resuming. If a memory adapter returns this checkpoint,
keep its source, scope and freshness with it; a checkpoint cannot grant a sending
tool, revive a cancelled request or override the current user's correction.
