from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path

MERGE_ROOT = Path(__file__).resolve().parents[1]
WORKTREE_ROOT = MERGE_ROOT.parent


class HistoricalVerifierTests(unittest.TestCase):
    @unittest.skipUnless((WORKTREE_ROOT / ".spike/local_results/evaluation").is_dir(), "historical dev artifacts unavailable")
    def test_read_only_verifier_accepts_kill_and_preserves_raw_evidence(self):
        raw = WORKTREE_ROOT / ".spike/local_results/evaluation/late_v8/resolution_dev/resolution_raw.json"
        before = hashlib.sha256(raw.read_bytes()).hexdigest()
        result = subprocess.run(
            [sys.executable, str(MERGE_ROOT / "verify_historical.py")],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "VERIFIED")
        self.assertEqual(payload["recommendation"], "KILL_NO_CANDIDATE_PASSED")
        self.assertEqual(payload["dev_records"], 1096)
        self.assertTrue(payload["read_only"])
        self.assertFalse(payload["frozen_access"])
        self.assertEqual(hashlib.sha256(raw.read_bytes()).hexdigest(), before)


if __name__ == "__main__":
    unittest.main()
