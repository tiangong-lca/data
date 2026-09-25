---
title: data Validation Guide
docType: guide
scope: repo
status: active
authoritative: true
owner: data
language: en
whenToUse:
  - when selecting validation for data, schema, stylesheet, release-note, or documentation-governance changes
  - when recording proof for repository-local docpact governance changes
whenToUpdate:
  - when a canonical validation command is added
  - when data or asset validation expectations change
  - when docpact governance rules or CI behavior change
checkPaths:
  - AGENTS.md
  - README.md
  - README_CN.md
  - .docpact/config.yaml
  - .github/workflows/publish.yml
  - .github/workflows/ai-doc-lint.yml
  - release.json
  - tiangong_lca_data/**
  - schemas/**
  - stylesheets/**
  - release_notes/**
  - .githooks/pre-push
  - scripts/docpact
  - scripts/docpact-gate.sh
  - scripts/install-git-hooks.sh
lastReviewedAt: 2026-09-25
lastReviewedCommit: 2e163304adb9357cd7a17facfc8e5b426ed74a93
lastReviewedNote: "Reviewed for Data #33 option A against exact origin/main: the user selected retirement of the unsupported active mine-water Process and retention of a separate historical Source for the unverified April 2019 draft-mirror row. XSD and public Toolkit 0.3.3 Source-only import/roundtrip passed with both languages retained. Shared Source 08a0183e remains unchanged for Data #35; mirror authenticity, LCDN/Platform disposition, Data PR and root integration are not claimed."
related:
  - AGENTS.md
  - .docpact/config.yaml
  - docs/agents/repo-architecture.md
---

# data Validation Guide

This repository is content-oriented and does not currently define a single checked-in green-bar wrapper such as `npm test`, `cargo test`, or `pytest`.

## Required Validation Shape

- Data payload changes require direct review of the touched files under `tiangong_lca_data/**`.
- Schema and stylesheet changes require reviewing the affected bundled assets and any data-package expectations they imply.
- Release metadata changes require checking that `release.json`, `release_notes/v<version>.md`, and the archived data snapshot agree. GitHub Release publishing must remain disabled.
- Documentation-governance changes require docpact validation.

## Docpact Validation

Run these commands for governance changes:

```bash
scripts/docpact validate-config --root . --strict
scripts/docpact lint --root . --base origin/main --head HEAD --mode enforce
```

The manual `ai-doc-lint` workflow delegates to the same local docpact gate when remote reproduction is needed.

## Future Automation

If this repository gains a canonical data validation wrapper later, update this file, `AGENTS.md`, and `.docpact/config.yaml` in the same change. The current publish workflow is a retired release notice, not release automation or a general data validation wrapper.

## Local Docpact Push Gate

Install the versioned local hook once per checkout:

```bash
./scripts/install-git-hooks.sh
```

The `pre-push` hook runs `scripts/docpact-gate.sh`, which delegates CLI lookup to `scripts/docpact` and performs strict config validation plus enforced lint before the push leaves the machine. The wrapper checks `DOCPACT_BIN`, Cargo install locations, Homebrew install locations, and then `PATH`, so local agent shells should not fail only because bare `docpact` is unavailable. The default comparison base is `origin/main`. Override it for unusual stacks with `DOCPACT_BASE_REF=<ref>` or `scripts/docpact-gate.sh --base <ref>`. The gate writes its detailed report to a temporary file so normal pushes do not create `.docpact/runs/` artifacts.
