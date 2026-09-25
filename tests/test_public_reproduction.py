"""Tests for the processed-data-only public statistical pipeline."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


class PublicReproductionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp = tempfile.TemporaryDirectory()
        cls.out = Path(cls.temp.name) / "first"
        subprocess.run([sys.executable, str(ROOT / "scripts/reproduce_public_results.py"),
                        "--output", str(cls.out)], check=True, stdout=subprocess.PIPE, text=True)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp.cleanup()

    def test_processed_inputs_load_and_controller_ids_match(self) -> None:
        controllers = read_csv(ROOT / "data/processed/controllers.csv")
        self.assertEqual([r["controller_id"] for r in controllers], [f"C{i:02d}" for i in range(1,10)])
        runs = read_csv(ROOT / "data/processed/runs.csv")
        self.assertEqual(len(runs), 11)
        self.assertEqual({r["controller_id"] for r in runs}, {r["controller_id"] for r in controllers})

    def test_transfer_matrix_dimensions_and_headline(self) -> None:
        for ch in ("r_y", "r_u", "joint"):
            matrix = read_csv(self.out / "tables" / f"far_matrix_{ch}.csv")
            self.assertEqual(len(matrix), 4)
            self.assertEqual(list(matrix[0]), ["calibration_controller"] + [f"C{i:02d}" for i in range(1,10)])
        effort = read_csv(self.out / "tables/far_matrix_r_u.csv")
        c04 = next(r for r in effort if r["calibration_controller"] == "C04")
        self.assertAlmostEqual(float(c04["C01"]), 0.14072916666666666)
        headline = json.loads((self.out / "tables/headline_results.json").read_text(encoding="utf-8"))
        self.assertEqual(round(100*headline["primary_effort_maximum_far"],2),14.07)

    def test_same_controller_maximum_and_run_pairs(self) -> None:
        runs = read_csv(self.out / "tables/table3_same_controller_runs.csv")
        self.assertEqual(len(runs),4)
        self.assertEqual({(r["calibration_run"],r["evaluation_run"]) for r in runs},
                         {("9","10"),("10","9"),("13","18"),("18","13")})
        self.assertEqual(round(100*max(float(r["r_u_far"]) for r in runs),2),1.39)

    def test_diversity_and_contrast(self) -> None:
        rows = read_csv(self.out / "tables/calibration_diversity_summary.csv")
        def worst(count: str) -> float:
            return next(float(r["worst_unseen_controller_far"]) for r in rows
                        if r["calibration_controller_count"] == count and
                        r["pooling_method"] == "EQUAL_CONTROLLER_FOUR_CYCLES" and r["channel"] == "r_u")
        self.assertEqual(round(100*worst("1"),2),45.86)
        self.assertEqual(round(100*worst("8"),2),3.76)
        headline = json.loads((self.out / "tables/headline_results.json").read_text(encoding="utf-8"))
        self.assertEqual([round(headline["calibration_error_contrast"][ch],2) for ch in
                          ("r_y","r_u","joint")],[5.20,3.31,3.26])

    def test_reciprocal_mechanism_and_far_target_ablation(self) -> None:
        mechanism = read_csv(self.out / "tables/reciprocal_score_mechanism.csv")
        effort = next(r for r in mechanism if r["direction"] == "C04_TO_C01" and r["channel"] == "r_u")
        self.assertEqual(round(float(effort["mad_ratio_target_over_source"]),2),2.39)
        self.assertEqual(round(float(effort["q99_ratio_target_over_source"]),2),2.42)
        ablation = read_csv(self.out / "tables/appendix_c_far_target_ablation.csv")
        self.assertEqual(len(ablation),4)
        self.assertEqual([round(100*float(r["r_u_maximum_far"]),2) for r in ablation],
                         [12.61,14.07,22.29,32.52])

    def test_fixed_seed_and_deterministic_tables(self) -> None:
        config = json.loads((ROOT / "config/release_analysis.json").read_text(encoding="utf-8"))
        self.assertEqual(config["random_seed"],33043)
        again = Path(self.temp.name) / "second"
        subprocess.run([sys.executable, str(ROOT / "scripts/reproduce_public_results.py"),
                        "--output", str(again)], check=True, stdout=subprocess.PIPE, text=True)
        for first in sorted((self.out / "tables").glob("*")):
            second = again / "tables" / first.name
            self.assertEqual(hashlib.sha256(first.read_bytes()).digest(),
                             hashlib.sha256(second.read_bytes()).digest(),first.name)
        for first in sorted((self.out / "figures").glob("*.png")):
            second = again / "figures" / first.name
            self.assertEqual(hashlib.sha256(first.read_bytes()).digest(),
                             hashlib.sha256(second.read_bytes()).digest(),first.name)

    def test_no_raw_or_course_payload(self) -> None:
        self.assertFalse((ROOT / ".git").exists())
        forbidden = {".mat", ".slx", ".bin", ".elf", ".hex", ".m"}
        self.assertFalse([p for p in ROOT.rglob("*") if p.is_file() and p.suffix.lower() in forbidden])


if __name__ == "__main__":
    unittest.main()
