# Exploratory ChatGPT response comparison

The comparison uses one trial for each combination of the 24 original public cases and three instructions, for 72 planned samples. The cases come from `evals/cases.jsonl` and include its smoke and development splits. They are public development material, so this design cannot estimate performance on a held-out sample.

The baseline uses `BASE` from `scripts/evaluate.py`. The brief condition adds `BRIEF` from that script. The UAI condition adds the exact runtime skill with SHA-256 `5633377efaaa9b85fd9ed0fddfb62e45fe0b3f8d9db3c1cd7dcf8088c849b3fd`. Every condition adds the same conversation serialized by the script's `prompt` function. The coordinator shuffled the case-condition pairs with Python `random.Random(20261125).shuffle`, then assigned opaque sample IDs in that order. No rubric, expected behavior, case category, case ID, or condition label was included in the actor request file.

Each actor is a fresh ChatGPT collaboration thread, created without inherited conversation history. The requested configuration is `gpt-6.2-sol` at high reasoning effort. The collaboration surface does not expose the resolved model or settings, so the ledgers record them as unknown. It also does not provide per-response token or provider latency measurements. The harness supplies instruction text to each actor in its request file. It does not exercise native skill installation or triggering.

Each actor has a separate directory outside the repository. The common wrapper instructs actors to read their own request, write the exact response to their response file, and avoid all other file access, browsing, agent calls, and external action. Isolation of tool use is prompt-enforced. The host still supplies system instructions and tools, and the operating system does not restrict each actor to its own directory. Cases and responses are synthetic.

The manifest records the queued samples and subsequent lifecycle events as append-only JSONL. The response ledger records each completed or failed attempt, exact response text when present, and its byte-level SHA-256. The input hash covers the exact request file. At most two actors may be active concurrently, subject to the collaboration cap. A failed actor may be replaced once after checking for its response file. Capacity errors before an actor starts do not count as sampled responses. Grading is outside the coordinator's scope.

The initial actor message uses the following text, with the request and response path replaced for each sample.

> Read only {request path}. Use its instructions to continue the supplied conversation and respond to its final user message. The supplied conversation has no task tools. Do not inspect other files, browse, invoke agents, or act on external systems. Your only permitted file operations are reading that request and writing the exact answer, with no wrapper, to {response path}. Then end your turn.

## Completed run

The selected ledger contains exactly one entry for each planned sample, 24 per condition. The attempt ledger contains 72 recorded outputs plus one interrupted attempt. Sample s015's first actor was interrupted before writing an answer, so the coordinator checked for the missing file and used the single permitted retry. The retry wrote an answer, and both attempts remain recorded. The selected ledger uses the latest attempt for each planned slot. An `ok` entry means the response was captured and verified against its file hash. It carries no behavioral grade.

## Independent blinded review and adjudication

A separate fresh ChatGPT agent received the conversation, exact response, original rubric and opaque sample ID. It did not receive condition labels, case IDs, the UAI instructions or the response metadata. Requested reviewer model: gpt-6.2-sol, high effort; resolved model/settings were not exposed. The judge produced one hash-linked semantic judgment for each response. This is agent review, not human evaluation. The integration agent then inspected all nine nonpasses and the deletion-target borderline cases. The original judgments are retained unchanged.

The integration review flags dev-12 as a fixture-validity concern: “and also” can reasonably request two separate outputs, which all three conditions produced. The frozen rubric instead requires treatment as a conflict. Smoke-05 and dev-13 additionally distinguish an explicit unavailable-source statement or request for evidence from useful implicit handling. These strict outcomes should not be presented as a general task-success estimate. No case, rubric or runtime instruction was changed to improve this run's score.

The baseline means no additional experimental UAI/brief instruction. Common host policies and customization can still apply, so this is not a bare-model baseline. Rubric isolation is prompt-enforced, not an operating-system security boundary. Role-tagged conversation is serialized into a request file rather than supplied as native host role messages. The harness loads SKILL.md only, not its optional reference files. There were no measurements of token use, latency, user satisfaction or native automatic skill selection.
