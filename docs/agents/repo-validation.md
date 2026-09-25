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
  - scripts/build-docpact-0.1.9.sh
  - scripts/patches/docpact-0.1.9-rev-list-stdin.patch
  - scripts/install-git-hooks.sh
lastReviewedAt: 2026-09-25
lastReviewedCommit: 06afbd82ccf33346c449405aaaeb35c5fd61b2a3
lastReviewedNote: "Reviewed for Data #39: exact-source Docpact 0.1.9 plus the checksum-pinned stdin pathspec patch runs strict config validation and enforced full-diff lint over the complete data checkout. The manual fallback retains the local gate, and no dataset, schema, or release payload changes are implied."
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
export DOCPACT_BIN="$(scripts/build-docpact-0.1.9.sh)"
scripts/docpact validate-config --root . --strict
scripts/docpact lint --root . --base origin/main --head HEAD --mode enforce
```

The pinned build checks the Docpact 0.1.9 source commit, source-file and lockfile SHA-256 values, the reviewed patch SHA-256, and the patched source SHA-256. It runs the upstream Rust tests and a locked release build. The patch changes only the Git freshness query transport: all tracked paths go to one `git rev-list --stdin` invocation, retaining merge-history semantics while avoiding OS argument limits. A newline-containing path fails closed. The manual `ai-doc-lint` workflow delegates to the same local docpact gate with this binary when remote reproduction is needed; it does not add a baseline, waiver, or dataset exclusion.

## Future Automation

If this repository gains a canonical data validation wrapper later, update this file, `AGENTS.md`, and `.docpact/config.yaml` in the same change. The current publish workflow is a retired release notice, not release automation or a general data validation wrapper.

## Local Docpact Push Gate

Install the versioned local hook once per checkout:

```bash
./scripts/install-git-hooks.sh
```

The `pre-push` hook runs `scripts/docpact-gate.sh`, which delegates CLI lookup to `scripts/docpact` and performs strict config validation plus enforced lint before the push leaves the machine. The wrapper checks `DOCPACT_BIN`, Cargo install locations, Homebrew install locations, and then `PATH`, so local agent shells should not fail only because bare `docpact` is unavailable. The default comparison base is `origin/main`. Override it for unusual stacks with `DOCPACT_BASE_REF=<ref>` or `scripts/docpact-gate.sh --base <ref>`. The gate writes its detailed report to a temporary file so normal pushes do not create `.docpact/runs/` artifacts.

For this large repository, export the binary path emitted by `scripts/build-docpact-0.1.9.sh` before any local push; stock 0.1.9 can otherwise fail with E2BIG during freshness evaluation. The build directory is outside the checkout and remains available for the shell's later gate invocations.
