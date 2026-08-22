import json, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]

class KitTests(unittest.TestCase):
    def test_registry_and_context(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "registry.toml"
            source.write_text((ROOT / "examples/minimal/registry.toml").read_text(), encoding="utf-8")
            subprocess.run([sys.executable, str(ROOT / "kit/registry.py"), str(source)], check=True)
            result = subprocess.run([sys.executable, str(ROOT / "kit/render_context.py"), str(source.with_suffix(".json"))], check=True, capture_output=True, text=True)
            self.assertIn("CT-2026-014", result.stdout)
            self.assertEqual(json.loads(source.with_suffix(".json").read_text())["schema_version"], 1)

    def test_refresh_isolated_pipeline(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fixture = ROOT / "examples/minimal/registry.toml"
            (root / "registry.toml").write_text(fixture.read_text(), encoding="utf-8")
            (root / "notes.md").write_text("TODO: review this item\n", encoding="utf-8")
            (root / "generated").mkdir()
            (root / "generated" / "old.txt").write_text("PENDING: stale derived output\n", encoding="utf-8")
            subprocess.run([sys.executable, str(ROOT / "kit/refresh.py"), str(root)], check=True)
            generated = root / "generated"
            self.assertEqual(
                json.loads((generated / "manifest.json").read_text())["artifacts"],
                ["registry.json", "observations.json", "context.txt", "context.html", "context.json"],
            )
            self.assertIn("observed_at", json.loads((generated / "observations.json").read_text()))
            self.assertIn("generated_at", json.loads((generated / "manifest.json").read_text()))
            self.assertIn("demo-project", (generated / "context.txt").read_text())
            self.assertIn("<table>", (generated / "context.html").read_text())
            self.assertEqual(json.loads((generated / "context.json").read_text())["schema_version"], 1)
            signals = json.loads((generated / "observations.json").read_text())["signals"]
            self.assertEqual(len(signals), 1)
            self.assertEqual(signals[0]["source"], str(root / "notes.md"))

    def test_registry_rejects_missing_lifecycle_fields(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "registry.toml"
            source.write_text('[[item]]\nid = "incomplete"\n', encoding="utf-8")
            result = subprocess.run([sys.executable, str(ROOT / "kit/registry.py"), str(source)], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("missing required field", result.stderr)

    def test_registry_rejects_duplicate_ids(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "registry.toml"
            source.write_text(
                '[[item]]\nid = "same"\nkind = "project"\nstate = "ACTIVE"\npriority = "LOW"\n\n'
                '[[item]]\nid = "same"\nkind = "project"\nstate = "ACTIVE"\npriority = "LOW"\n',
                encoding="utf-8",
            )
            result = subprocess.run([sys.executable, str(ROOT / "kit/registry.py"), str(source)], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("duplicate item id", result.stderr)

if __name__ == "__main__":
    unittest.main()
