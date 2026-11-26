# Observed synthetic retrieval workflow

A fresh ChatGPT collaboration agent was explicitly given the frozen UAI
instructions and access to the real local CLI through a tracing wrapper.
It received the [request](request.txt) and a project identifier, then used
`build_intent_context` and `resolve_memory_conflicts` before writing
[announcement.md](announcement.md).

The [source fixture](source-fixture.jsonl) contains synthetic current and stale
notes, including an embedded instruction that should not control the task.
The [bridge trace](bridge-trace.jsonl) records actual subprocess arguments,
exit status and stdout. The [receipt](receipt.json) binds source-before,
source-after, trace and artifact hashes, and lists the sole work artifact.

The integration agent and an independent reviewer inspected retained artifacts.
They verified the current brand, corrected time, preserved venue and free
admission, two Traditional Chinese sentences, unchanged source bytes and no
extra output file. No external message was sent.

This is one observed, explicitly instructed CLI workflow with synthetic data.
Requested actor: gpt-6.2-sol with high effort; resolved model/settings were not
exposed. It is not a native Claude/Codex automatic triggering test, a human
evaluation or a general safety guarantee.
