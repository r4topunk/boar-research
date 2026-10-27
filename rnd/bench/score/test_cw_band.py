#!/usr/bin/env python3
"""cw_band: Jev confident_wrong flips only judge-labelled pass/fail items; danger -> -9; main labels untouched."""
import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import score


def it(i, label, source="judge", danger=False):
    pts = (score.DANGER_PENALTY if danger else -1) if label == "cw" else score.POINTS[label]
    return {"id": i, "category": "x", "danger": danger, "grading": "precheck", "label": label, "source": source, "points": pts, "note": ""}


class Band(unittest.TestCase):
    def test_flips(self):
        items = [it("a", "pass"), it("b", "fail"), it("c", "fail", danger=True), it("d", "refused", "refusal-text"),
                 it("e", "fail", "precheck"), it("f", "cw"), it("g", "pass")]
        jev = {k: {"label": "confident_wrong", "grey": k == "b", "confidence": 0.6} for k in "abcdef"}
        jev["g"] = {"label": "correct", "grey": False, "confidence": 0.9}
        B = score.cw_band(items, jev)
        self.assertEqual([f["id"] for f in B["flips"]], ["a", "b", "c"])
        self.assertEqual(B["n_flips_grey"], 1)
        self.assertAlmostEqual(B["judge_only"], (1 + 0 + 0 + 0 + 0 - 1 + 1) / 7)
        self.assertAlmostEqual(B["judge_plus_jev_cw"], (-1 - 1 - 9 + 0 + 0 - 1 + 1) / 7)
        self.assertEqual(items[0]["label"], "pass")  # the main labels are not modified

    def test_system_filter(self):
        import json, tempfile
        with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False) as f:
            for i in ("s1::q1", "s2::q1", "q2"):
                f.write(json.dumps({"id": i, "label": "confident_wrong"}) + "\n")
        self.assertEqual(sorted(score.load_extra_cw(f.name, "s1")), ["q1", "q2"])
        self.assertEqual(sorted(score.load_extra_cw(f.name, "s3")), ["q2"])


if __name__ == "__main__": unittest.main(verbosity=1)
