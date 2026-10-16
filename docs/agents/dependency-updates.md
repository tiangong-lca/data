---
title: Data Automation Dependency Updates
docType: guide
scope: repo
status: active
authoritative: false
owner: data
language: en
whenToUse:
  - when reviewing GitHub Actions or dependency workflow changes
  - when changing dependency monitoring or ordinary PR automation checks
whenToUpdate:
  - when monitoring cadence, validation scope or tool installation changes
checkPaths:
  - .github/dependabot.yml
  - .github/workflows/dependency-pr.yml
  - docs/agents/dependency-updates.md
lastReviewedAt: 2026-10-16
lastReviewedCommit: c50cab7961e0b0ca11c26a600bd4c90fea6c6c32
lastReviewedNote: "Data #43 adds Actions-only monitoring and read-only PR checks using actionlint and existing identity-verifier tests; dataset assets, exact attestation and retired publishing remain unchanged."
related:
  - ../../AGENTS.md
  - ./repo-validation.md
---

# Automation Dependency Updates

This repository has no application dependency manifest. Dependabot monitors
GitHub Actions only, on Thursdays at 05:00 in Asia/Shanghai, with a seven-day
cooldown and one open version-update PR. Actions updates share one review group.
Automatic merging is not configured. The version schedule and cooldown do not
delay security updates.

The separate `Dependency workflow validation` workflow runs for main-target PRs
touching Dependabot configuration, workflows or `.github/scripts/**`, and supports
manual validation. It checks out the exact candidate with no persisted credentials,
has only `contents: read`, and cancels superseded runs for the same PR. It validates
workflow definitions with the exact actionlint release and Linux archive digest
declared in the workflow, then runs the existing Python standard-library tests for
the attestation identity verifier.

actionlint checks workflow syntax, contexts, expressions and job contracts without
executing the workflows it reads. Optional ShellCheck and Pyflakes integrations
are disabled so this check does not introduce additional runtime/tool dependencies.
Local validation uses the actionlint version pinned by the workflow:

```bash
actionlint -shellcheck= -pyflakes=
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s .github/scripts -p 'test_attest_merged_pr.py' -v
```

Changing the tool version requires checking the current stable official release,
its immutable archive digest, and compatibility with the existing workflows.
The direct actionlint binary pin is maintained manually; Actions monitoring
updates the action references.
References: [actionlint installation](https://github.com/rhysd/actionlint/blob/main/docs/install.md),
[actionlint releases](https://github.com/rhysd/actionlint/releases), and
[Dependabot options](https://docs.github.com/en/code-security/reference/supply-chain-security/dependabot-options-reference).

The PR check does not dispatch attestation, publish a commit status, sign or upload
data, build Docpact, regenerate data, or run retired publishing. The existing
`attest-merged-pr.yml` remains manual-only with its trusted-main validation and
separate status-only publisher. Its unit tests prove identity rejection behavior;
they do not execute that publisher. Dataset, schema/style, digest and scientific
review obligations retain their existing contracts.

Monitoring takes effect from `main`. A passing local check and merged configuration
do not prove that the first updater or resulting dependency PR ran; inspect those
GitHub records and repository security settings separately. Governance validation
still uses the checksum-pinned corrected Docpact build described in
[the validation guide](repo-validation.md), including the complete governed dataset.
