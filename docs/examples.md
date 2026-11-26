# Three worked examples

These are synthetic illustrations of the intended workflow, not claims that
UAI outperforms another model. Published response and tool evidence is linked
from [verification](verification.md).

## 1. A multilingual correction

**Context:** A workshop announcement says 10:00, Room 3, free admission.

**User:** 「改成繁體中文，兩句。時間改 11:00，Room 3 同免費 keep。」

**Useful result:** A two-sentence Traditional Chinese announcement with 11:00,
Room 3 and free admission. No interview about tone is required for this small
rewrite. The corrected time replaces only the original time.

## 2. Status, correction, then continuation

**Active task:** Draft a short event announcement and check its time and room.
The user requested a draft only.

**User:** “How far along are you? Also change the time to 11:00. Continue.”

**Useful result:** Briefly state verified progress, apply the time correction,
and finish the remaining draft/check. Preserve the room and the draft-only
boundary. A status question does not cancel the work, and a prior assistant's
“done” message does not establish that a check actually happened.

**If the next message is “Cancel that; explain the options instead”:** Stop the
pending draft actions and answer the new question. An old checkpoint must not
revive the cancelled work.

## 3. Current instruction versus old memory

**Available memory:** An older note says the project brand is Ember Notes.
A later source records Aurora Notes. Both retain provenance; a timestamp alone
does not authenticate either statement.

**User:** “Use Aurora Notes in this draft. Keep the venue and free admission.”

**Useful result:** Use Aurora Notes and preserve the other facts. The current
explicit correction resolves the wording. If an essential detail is still
missing, `build_intent_context` can retrieve relevant records from the configured
project. Unresolved keyed conflicts remain visible rather than silently choosing
a winner.

Try the actual retrieval behavior with:

```sh
python3 scripts/demo_context.py
```

The demo creates its own fixtures, exercises all eight CLI operations, verifies
unchanged source bytes during retrieval, and checks expiry, conflicts, long
records, stale IDs and unavailable sources. Add `--mcp` after installing the
optional SDK to exercise real stdio initialization, tool discovery and retrieval.
The demo does not invoke a model or read personal memory.
