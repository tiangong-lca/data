#!/usr/bin/env python3
"""Verify an immutable, same-repository merged PR before exact-head linting.

This file is loaded only from the workflow's trusted main checkout. The candidate
checkout supplies data to Docpact but never supplies executable validation code.
"""

import json
import os
import re
import sys
import urllib.error
import urllib.request


REPOSITORY = "tiangong-lca/data"
SHA = re.compile(r"[0-9a-f]{40}\Z")
PR_NUMBER = re.compile(r"[1-9][0-9]*\Z")
QUERY = """
query($number: Int!) {
  repository(owner: "tiangong-lca", name: "data") {
    nameWithOwner
    pullRequest(number: $number) {
      number
      state
      mergedAt
      baseRefName
      baseRefOid
      headRefOid
      baseRepository { nameWithOwner }
      headRepository { nameWithOwner }
      mergeCommit { oid }
    }
  }
}
"""


def require(condition, message):
    if not condition:
        raise ValueError(message)


def dispatch_inputs(env):
    require(env.get("GITHUB_EVENT_NAME") == "workflow_dispatch", "Expected workflow_dispatch")
    require(env.get("GITHUB_REF") == "refs/heads/main", "Dispatch must use main")
    require(env.get("GITHUB_REPOSITORY") == REPOSITORY, "Unexpected workflow repository")
    number = env.get("PR_NUMBER", "")
    require(bool(PR_NUMBER.fullmatch(number)) and int(number) <= 2_147_483_647, "Invalid PR number")
    expected = {}
    for key in ("EXPECTED_BASE", "EXPECTED_HEAD", "EXPECTED_MERGE"):
        value = env.get(key, "")
        require(bool(SHA.fullmatch(value)), f"Invalid {key} SHA")
        expected[key] = value
    require(bool(env.get("GITHUB_TOKEN")), "Read-only GitHub token is required")
    return int(number), expected


def verify_pull_request(payload, number, expected):
    require(not payload.get("errors"), "GraphQL returned errors")
    repository = (payload.get("data") or {}).get("repository") or {}
    require(repository.get("nameWithOwner") == REPOSITORY, "Repository identity mismatch")
    pr = repository.get("pullRequest") or {}
    require(pr.get("number") == number, "PR number mismatch")
    require(pr.get("state") == "MERGED" and pr.get("mergedAt"), "PR is not merged")
    require(pr.get("baseRefName") == "main", "PR target is not main")
    require((pr.get("baseRepository") or {}).get("nameWithOwner") == REPOSITORY, "PR base repository mismatch")
    require((pr.get("headRepository") or {}).get("nameWithOwner") == REPOSITORY, "Fork heads are not eligible")
    require(pr.get("baseRefOid") == expected["EXPECTED_BASE"], "Original PR base SHA mismatch")
    require(pr.get("headRefOid") == expected["EXPECTED_HEAD"], "PR head SHA mismatch")
    require((pr.get("mergeCommit") or {}).get("oid") == expected["EXPECTED_MERGE"], "PR merge commit mismatch")
    return {
        "pr": number,
        "base": expected["EXPECTED_BASE"],
        "head": expected["EXPECTED_HEAD"],
        "merge": expected["EXPECTED_MERGE"],
    }


def fetch_pull_request(number, token):
    body = json.dumps({"query": QUERY, "variables": {"number": number}}).encode("utf-8")
    request = urllib.request.Request(
        "https://api.github.com/graphql",
        data=body,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "data-exact-merged-pr-attestation",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def main():
    number, expected = dispatch_inputs(os.environ)
    verified = verify_pull_request(fetch_pull_request(number, os.environ["GITHUB_TOKEN"]), number, expected)
    output = os.environ["GITHUB_OUTPUT"]
    with open(output, "a", encoding="utf-8") as file:
        for key, value in verified.items():
            file.write(f"{key}={value}\n")
    print(f"Verified merged PR #{number}: base={verified['base']} head={verified['head']} merge={verified['merge']}")


if __name__ == "__main__":
    try:
        main()
    except (KeyError, ValueError, urllib.error.URLError) as error:
        print(f"Exact merged PR verification failed: {error}", file=sys.stderr)
        sys.exit(1)
