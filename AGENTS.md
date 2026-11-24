# Contributor instructions

This repository is the canonical public source for Understanding Ambiguous Intent.

- Keep the runtime skill concise and host-neutral.
- Do not add personal history, credentials, telemetry, or required hosted services.
- Keep evaluation rubrics and outputs outside skills/.
- Use local validation; do not introduce GitHub Actions.
- Before release, run python3 scripts/check.py and python3 -m unittest discover -s tests.
- Changes to behavior need a concrete case and truthful evidence, including regressions.
- Do not claim installation, triggering, or task execution from a text-only test.
- VERSION is the release version. Keep plugin manifests and release notes aligned.
- Do not edit evaluation answers or judge criteria merely to improve a score.
