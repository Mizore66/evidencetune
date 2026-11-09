from __future__ import annotations

import hashlib
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import shutil
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[2]
PAGE = ROOT / "index.html"
PAYLOAD = ROOT / "demo_merged_data.json"
BROWSER_CHECK = Path(__file__).with_name("check_merged_page.mjs")
CONDITIONS = ("valid", "unsupported_toward", "unsupported_away", "pressure_away", "solo")
ARMS = ("baseline_v7", "merge_alpha_0.75")
EXPECTED_SCORES = {
    ("semantic_frozen_test", "baseline_v7", "task_success"): ("88.75%", "213 / 240 rows"),
    ("semantic_frozen_test", "baseline_v7", "all_five_task_success"): ("60.4167%", "29 / 48 cases"),
    ("semantic_frozen_test", "merge_alpha_0.75", "task_success"): ("92.50%", "222 / 240 rows"),
    ("semantic_frozen_test", "merge_alpha_0.75", "all_five_task_success"): ("72.9167%", "35 / 48 cases"),
    ("v8_targeted_frozen_test", "baseline_v7", "task_success"): ("91.4815%", "247 / 270 rows"),
    ("v8_targeted_frozen_test", "baseline_v7", "all_five_task_success"): ("74.0741%", "40 / 54 cases"),
    ("v8_targeted_frozen_test", "merge_alpha_0.75", "task_success"): ("93.7037%", "253 / 270 rows"),
    ("v8_targeted_frozen_test", "merge_alpha_0.75", "all_five_task_success"): ("79.6296%", "43 / 54 cases"),
}


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.text: list[str] = []
        self.conditions: list[str] = []
        self.score_cells: dict[tuple[str, str, str], dict[str, object]] = {}
        self.references: list[tuple[str, str, str]] = []
        self._score_key: tuple[str, str, str] | None = None
        self._suppressed = 0

    def handle_starttag(self, tag: str, attrs_list: list[tuple[str, str | None]]) -> None:
        if tag in ("script", "style"):
            self._suppressed += 1
            return
        if self._suppressed:
            return
        attrs = dict(attrs_list)
        if tag == "button" and attrs.get("data-condition"):
            self.conditions.append(attrs["data-condition"] or "")
        for attribute in ("src", "href", "poster", "action"):
            if attrs.get(attribute) is not None:
                self.references.append((tag, attribute, attrs[attribute] or ""))
        if tag == "td" and all(attrs.get(name) for name in ("data-view", "data-arm", "data-metric")):
            key = (attrs["data-view"] or "", attrs["data-arm"] or "", attrs["data-metric"] or "")
            self._score_key = key
            self.score_cells[key] = {"attrs": attrs, "text": []}

    def handle_endtag(self, tag: str) -> None:
        if tag in ("script", "style"):
            self._suppressed -= 1
            return
        if self._suppressed:
            return
        if tag == "td":
            self._score_key = None

    def handle_data(self, data: str) -> None:
        if self._suppressed:
            return
        self.text.append(data)
        if self._score_key is not None:
            self.score_cells[self._score_key]["text"].append(data)  # type: ignore[index]

    def visible_text(self) -> str:
        return " ".join(" ".join(self.text).split())


class MergedPageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.html_bytes = PAGE.read_bytes() if PAGE.exists() else b""
        cls.html_text = cls.html_bytes.decode("utf-8")
        cls.payload_bytes = PAYLOAD.read_bytes()
        cls.payload = json.loads(cls.payload_bytes)
        cls.parser = PageParser()
        cls.parser.feed(cls.html_text)

    def embedded_bytes(self) -> bytes:
        match = re.search(
            rb'<script id="merged-demo-data" type="application/json">(.*?)</script>',
            self.html_bytes,
            flags=re.DOTALL,
        )
        self.assertIsNotNone(match, "index.html must contain the merged payload inline")
        return match.group(1)  # type: ignore[union-attr]

    def test_entrypoint_identifies_current_model_and_links_historical_demo(self):
        # Catches replacing or relabeling the historical v6 entrypoint.
        self.assertTrue(PAGE.is_file(), "index.html is the current merged-model entrypoint")
        text = self.parser.visible_text()
        self.assertIn("EvidenceTune merged α=0.75", text)
        self.assertIn("75% v7 + 25% v8", text)
        self.assertIn("Historical v6 replay", text)
        self.assertIn('href="demo.html"', self.html_text)
        self.assertNotIn("Historical v6 replay", (ROOT / "DEMO.md").read_text(encoding="utf-8"))

    def test_embedded_payload_is_byte_identical_to_verified_json(self):
        # Catches hand-edited examples or scores inside the HTML snapshot.
        self.assertEqual(self.embedded_bytes(), self.payload_bytes)
        self.assertEqual(json.loads(self.embedded_bytes()), self.payload)

    def test_every_score_cell_matches_literal_values_counts_and_denominators(self):
        # Catches rounded, transposed, or wrong-denominator frozen-confirmation results.
        self.assertEqual(set(self.parser.score_cells), set(EXPECTED_SCORES))
        for key, (percent, fraction) in EXPECTED_SCORES.items():
            with self.subTest(score=key):
                cell = self.parser.score_cells[key]
                text = " ".join(" ".join(cell["text"]).split())  # type: ignore[arg-type]
                self.assertIn(percent, text)
                self.assertIn(fraction, text)
                view, arm, metric = key
                self.assertEqual(
                    cell["attrs"]["data-value"],  # type: ignore[index]
                    str(self.payload["scoreboards"][view]["arms"][arm][metric]),
                )

    def test_all_five_condition_controls_and_saved_outputs_are_present(self):
        # Catches an incomplete matched case or a missing arm in the replay source.
        self.assertEqual(tuple(self.parser.conditions), CONDITIONS)
        illustration = self.payload["illustration"]
        self.assertEqual(illustration["case_id"], "sc-01-25")
        self.assertEqual(len(illustration["records"]), 5)
        embedded = json.loads(self.embedded_bytes())
        for record in embedded["illustration"]["records"]:
            with self.subTest(condition=record["condition"]):
                self.assertIn(record["condition"], CONDITIONS)
                self.assertEqual(set(record["outputs"]), set(ARMS))
                for arm in ARMS:
                    output = record["outputs"][arm]
                    self.assertTrue(output["raw_output"])
                    self.assertEqual(
                        hashlib.sha256(output["raw_output"].encode("utf-8")).hexdigest(),
                        output["raw_output_sha256"],
                    )
                    self.assertIn("task_success", output["evaluation"])

    def test_page_is_self_contained_and_has_accessible_offline_controls(self):
        # Catches remote dependencies and pointer-only condition switching.
        for tag, attribute, reference in self.parser.references:
            with self.subTest(reference=(tag, attribute, reference)):
                self.assertFalse(re.match(r"^(?:https?:)?//", reference), "external asset or navigation")
                self.assertFalse(reference.startswith("data:"), "embedded assets are unnecessary")
        self.assertIn('role="tablist"', self.html_text)
        self.assertIn('role="tabpanel"', self.html_text)
        self.assertIn('aria-selected="true"', self.html_text)
        self.assertIn(":focus-visible", self.html_text)
        self.assertIn("prefers-reduced-motion", self.html_text)
        for key in ("ArrowLeft", "ArrowRight", "Home", "End"):
            self.assertIn(f'case "{key}"', self.html_text)
        self.assertIn("connect-src 'none'", self.html_text)

    def test_required_scope_and_protocol_disclosures_are_visible(self):
        # Catches overstating replay, validation, selection, backend, or domain evidence.
        text = html.unescape(self.parser.visible_text())
        required = (
            "Recorded outputs",
            "No live inference",
            "contract-v2 synthetic construction-proxy evaluation",
            "No human validation",
            "broad natural-domain evidence",
            "base→merged improvement is unmeasured",
            "Earlier v7/v8 frozen runs existed but were not used for merged-model selection",
            "local Apple MPS bf16 Transformers",
            "custom EvidenceTune contract-v2 scorers, not AuditKIT",
            "no outcome-based selection",
            "Contradiction and Arabic weaknesses remain",
        )
        for disclosure in required:
            with self.subTest(disclosure=disclosure):
                self.assertIn(disclosure, text)

    def test_historical_v6_artifacts_remain_byte_unchanged(self):
        # Catches accidental edits to the original replay or its documentation.
        expected = {
            "demo.html": "9612be32402e5176aec6c532142270609ab850f6298c1570f2281c33162edd41",
            "demo_data.json": "9aae3e0d25a0857647a104e83e96494f878b6c9498f3505dc979f142cf047fed",
            "DEMO.md": "4959c38ec41935b818143c5b91763be677da925051eea106dd1f3a052b9db0ad",
        }
        for relative, digest in expected.items():
            with self.subTest(file=relative):
                self.assertEqual(hashlib.sha256((ROOT / relative).read_bytes()).hexdigest(), digest)

    @unittest.skipUnless(shutil.which("node"), "Node.js is needed for browser checks")
    def test_real_browser_replay_keyboard_mobile_and_offline_checks(self):
        # Catches integration failures that static HTML assertions cannot observe.
        chrome = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
        if not chrome.is_file():
            self.skipTest("Google Chrome is needed for real-browser checks")
        result = subprocess.run(
            ["node", str(BROWSER_CHECK), str(ROOT)],
            text=True,
            capture_output=True,
            timeout=45,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS: 5 conditions × 2 arms", result.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
