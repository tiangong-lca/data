import unittest

from attest_merged_pr import dispatch_inputs, verify_pull_request


BASE = "2e163304adb9357cd7a17facfc8e5b426ed74a93"
HEAD = "6ae629498d6700b8792f5b9538ef1a9584bf277c"
MERGE = "06afbd82ccf33346c449405aaaeb35c5fd61b2a3"
EXPECTED = {"EXPECTED_BASE": BASE, "EXPECTED_HEAD": HEAD, "EXPECTED_MERGE": MERGE}


def payload(**changes):
    pr = {
        "number": 38,
        "state": "MERGED",
        "mergedAt": "2026-09-25T04:11:34Z",
        "baseRefName": "main",
        "baseRefOid": BASE,
        "headRefOid": HEAD,
        "baseRepository": {"nameWithOwner": "tiangong-lca/data"},
        "headRepository": {"nameWithOwner": "tiangong-lca/data"},
        "mergeCommit": {"oid": MERGE},
    }
    pr.update(changes)
    return {"data": {"repository": {"nameWithOwner": "tiangong-lca/data", "pullRequest": pr}}}


class ExactMergedPrTests(unittest.TestCase):
    def test_accepts_exact_merged_same_repository_head(self):
        self.assertEqual(verify_pull_request(payload(), 38, EXPECTED)["head"], HEAD)

    def test_rejects_untrusted_or_changed_identity(self):
        bad = [
            payload(state="OPEN"),
            payload(baseRefName="dev"),
            payload(baseRefOid="0" * 40),
            payload(headRefOid="0" * 40),
            payload(mergeCommit={"oid": "0" * 40}),
            payload(headRepository={"nameWithOwner": "another/data"}),
            payload(baseRepository={"nameWithOwner": "another/data"}),
            payload(number=39),
            {"errors": [{"message": "rate limited"}]},
        ]
        for case in bad:
            with self.subTest(case=case), self.assertRaises(ValueError):
                verify_pull_request(case, 38, EXPECTED)

    def test_dispatch_requires_main_and_exact_hex_inputs(self):
        env = {
            "GITHUB_EVENT_NAME": "workflow_dispatch",
            "GITHUB_REF": "refs/heads/main",
            "GITHUB_REPOSITORY": "tiangong-lca/data",
            "GITHUB_TOKEN": "test-token",
            "PR_NUMBER": "38",
            **EXPECTED,
        }
        self.assertEqual(dispatch_inputs(env)[0], 38)
        for key, value in [("GITHUB_REF", "refs/heads/feature"), ("PR_NUMBER", "0"), ("PR_NUMBER", "38; echo bad"), ("EXPECTED_HEAD", "A" * 40)]:
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                dispatch_inputs({**env, key: value})


if __name__ == "__main__":
    unittest.main()
