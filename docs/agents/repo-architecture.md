---
title: data Repo Architecture
docType: reference
scope: repo
status: active
authoritative: true
owner: data
language: en
whenToUse:
  - when determining whether a data, schema, stylesheet, or release-note change belongs in this repository
  - when checking source-of-truth boundaries between data, TIDAS, tooling, product UI, and workspace integration
whenToUpdate:
  - when dataset payload ownership changes
  - when bundled schema or stylesheet assets are reorganized
  - when cross-repo ownership boundaries change
checkPaths:
  - AGENTS.md
  - README.md
  - README_CN.md
  - .docpact/config.yaml
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
lastReviewedNote: "Reviewed the local Data #33 retirement candidate against exact origin/main: the unsupported mine-water Process is removed from active XML, while a new, separate Source preserves the unverified April 2019 draft-mirror row and its limits. XSD and published Toolkit 0.3.3 Source-only import and validation passed with both languages retained. Shared Source 08a0183e remains unchanged for Data #35; scientific approval, platform withdrawal, PR and workspace integration are not claimed."
related:
  - AGENTS.md
  - .docpact/config.yaml
  - docs/agents/repo-validation.md
---

# data Repo Architecture

`tiangong-lca-data` owns checked-in TianGong LCA dataset content and bundled reference assets that ship with the dataset package.

## Owned Surfaces

- `tiangong_lca_data/**` is the checked-in dataset payload and bundled package content.
- `schemas/**` contains schema reference files that travel with the data repository.
- `stylesheets/**` contains transformation or presentation assets that ship with the data repository.
- `release.json` records the historical dataset release version retained with archived release metadata.
- `release_notes/**` records archived versioned data release notes and release history.
- `README.md`, `README_CN.md`, and `wechat.jpg` are human-facing repository context and assets.

## Release Architecture

GitHub Release publishing is retired as of 2026-06-21. `.github/workflows/publish.yml` is retained only as a manual notice workflow and must not create tags, zip dataset payloads, publish GitHub Releases, or upload release assets.

Current TianGong LCA data access belongs to the TianGong LCA Platform at https://lca.tiangong.earth/, where users export the needed data through the platform export flow. `release.json` and `release_notes/**` remain in this repository only to preserve the historical release record.

## Non-Owner Boundaries

- `tiangong-lca-next` owns application UI and product workflow behavior.
- `tidas` owns TIDAS specification truth.
- `tidas-tools` owns conversion, validation, and export tooling implementation.
- `lca-workspace` owns root integration state and submodule pointer updates.

Do not infer app behavior, TIDAS semantics, conversion logic, or workspace delivery completion from this repository alone.

## Integration Semantics

A merged PR in this repository is repo-complete only. If the dataset snapshot must ship through the workspace, the root workspace must deliberately update the `tiangong-lca-data` submodule pointer after merge.

## Local Docpact Push Gate

This repository has a versioned local `pre-push` hook under `.githooks/pre-push` that delegates to `scripts/docpact-gate.sh`. The gate resolves the CLI through `scripts/docpact`, so local agent shells do not need bare `docpact` on `PATH`. The hook is a local developer guard for docpact config validation and enforced doc-governance linting; ordinary PRs and pushes rely on the local gate; `.github/workflows/ai-doc-lint.yml` is manual-dispatch fallback for remote reproduction.
