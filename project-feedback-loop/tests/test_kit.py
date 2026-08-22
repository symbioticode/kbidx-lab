import json
import subprocess
import sys
import tempfile
import unittest
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
            (root / "STATUS.md").write_text("TODO: update deployment state\n", encoding="utf-8")
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
            self.assertFalse((generated / ".manifest.json.tmp").exists())
            self.assertIn("demo-project", (generated / "context.txt").read_text())
            self.assertIn("observations: 2 | observed_at:", (generated / "context.txt").read_text())
            self.assertIn("demo-project | project | ACTIVE | priority=HIGH | signals=1", (generated / "context.txt").read_text())
            self.assertIn("<table>", (generated / "context.html").read_text())
            self.assertIn("<th>Match</th>", (generated / "context.html").read_text())
            self.assertIn("source_match", (generated / "context.json").read_text())
            machine = json.loads((generated / "context.json").read_text())
            self.assertEqual(machine["schema_version"], 1)
            self.assertEqual(machine["observation_count"], 2)
            self.assertIn("observed_at", machine)
            self.assertIn("markers", machine)
            signals = json.loads((generated / "observations.json").read_text())["signals"]
            self.assertEqual(len(signals), 2)
            self.assertEqual({signal["source"] for signal in signals}, {str(root / "notes.md"), str(root / "STATUS.md")})

    def test_failed_refresh_invalidates_old_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / "generated"
            output.mkdir()
            (output / "manifest.json").write_text('{"stale": true}\n', encoding="utf-8")
            (root / "registry.toml").write_text("[[item]]\nid = 42\n", encoding="utf-8")
            result = subprocess.run([sys.executable, str(ROOT / "kit/refresh.py"), str(root)], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((output / "manifest.json").exists())

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

    def test_registry_rejects_empty_registry(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "registry.toml"
            source.write_text("", encoding="utf-8")
            result = subprocess.run([sys.executable, str(ROOT / "kit/registry.py"), str(source)], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("one or more", result.stderr)

    def test_registry_rejects_non_string_required_fields(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "registry.toml"
            source.write_text('[[item]]\nid = 42\nkind = "project"\nstate = "ACTIVE"\npriority = "LOW"\n', encoding="utf-8")
            result = subprocess.run([sys.executable, str(ROOT / "kit/registry.py"), str(source)], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("missing required field", result.stderr)

    def test_portfolio_preserves_workspace_origin(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workspaces = []
            for name, item_id, priority in (("alpha", "P-1", "LOW"), ("beta", "CT-2", "HIGH")):
                workspace = root / name
                workspace.mkdir()
                (workspace / "registry.toml").write_text(
                    f'[[item]]\nid = "{item_id}"\nkind = "project"\nstate = "ACTIVE"\npriority = "{priority}"\n',
                    encoding="utf-8",
                )
                workspaces.append(str(workspace))
            output = root / "portfolio"
            subprocess.run([sys.executable, str(ROOT / "kit/portfolio.py"), *workspaces, "--output", str(output), "--marker", "REVIEW", "--exclude-dir", "node_modules"], check=True)
            data = json.loads((output / "portfolio.json").read_text())
            self.assertEqual(data["workspaces"], ["alpha", "beta"])
            self.assertEqual(data["markers"], {"alpha": ["REVIEW"], "beta": ["REVIEW"]})
            self.assertIn("generated_at", data)
            self.assertEqual(set(data["observed_at"]), {"alpha", "beta"})
            self.assertTrue(all(item["workspace_observed_at"] != "unknown" for item in data["items"]))
            self.assertEqual([(item["workspace"], item["id"]) for item in data["items"]], [("beta", "CT-2"), ("alpha", "P-1")])
            rendered = (output / "portfolio.html").read_text()
            self.assertIn("Portfolio context", rendered)
            self.assertIn("Generated at:", rendered)
            self.assertIn("Workspaces: alpha, beta", rendered)
            self.assertIn("Markers: alpha: REVIEW; beta: REVIEW", rendered)
            self.assertIn("Excluded directories: alpha: node_modules; beta: node_modules", rendered)
            manifest = json.loads((output / "manifest.json").read_text())
            self.assertEqual(manifest["artifacts"], ["portfolio.json", "portfolio.html"])
            self.assertEqual(manifest["workspaces"], ["alpha", "beta"])
            self.assertFalse((output / ".manifest.json.tmp").exists())

    def test_portfolio_forwards_excluded_directories(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workspace = root / "alpha"
            workspace.mkdir()
            (workspace / "registry.toml").write_text('[[item]]\nid = "P-1"\nkind = "project"\nstate = "ACTIVE"\npriority = "LOW"\n', encoding="utf-8")
            noisy = workspace / "node_modules"
            noisy.mkdir()
            (noisy / "dependency.md").write_text("TODO: ignored dependency\n", encoding="utf-8")
            output = root / "portfolio"
            subprocess.run([sys.executable, str(ROOT / "kit/portfolio.py"), str(workspace), "--output", str(output), "--exclude-dir", "node_modules"], check=True)
            data = json.loads((output / "portfolio.json").read_text())
            self.assertEqual(data["items"][0]["signal_count"], 0)
            self.assertEqual(data["excluded_dirs"]["alpha"], ["node_modules"])

    def test_portfolio_can_keep_workspace_outputs_external(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workspace = root / "alpha"
            workspace.mkdir()
            (workspace / "registry.toml").write_text('[[item]]\nid = "P-1"\nkind = "project"\nstate = "ACTIVE"\npriority = "LOW"\n', encoding="utf-8")
            output_root = root / "workspace-outputs"
            portfolio_output = root / "portfolio"
            subprocess.run([sys.executable, str(ROOT / "kit/portfolio.py"), str(workspace), "--workspace-output-root", str(output_root), "--output", str(portfolio_output)], check=True)
            self.assertTrue((output_root / "alpha/context.json").exists())
            self.assertFalse((workspace / "generated").exists())

    def test_portfolio_html_escapes_declared_values(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workspace = root / "alpha"
            workspace.mkdir()
            (workspace / "registry.toml").write_text(
                '[[item]]\nid = "<script>alert(1)</script>"\nkind = "project"\nstate = "ACTIVE"\npriority = "HIGH"\n',
                encoding="utf-8",
            )
            output = root / "portfolio"
            subprocess.run([sys.executable, str(ROOT / "kit/portfolio.py"), str(workspace), "--output", str(output)], check=True)
            rendered = (output / "portfolio.html").read_text(encoding="utf-8")
            self.assertNotIn("<script>alert(1)</script>", rendered)
            self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", rendered)

    def test_portfolio_rejects_duplicate_workspace_names(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = root / "one" / "same"
            second = root / "two" / "same"
            for workspace in (first, second):
                workspace.mkdir(parents=True)
                (workspace / "registry.toml").write_text('[[item]]\nid = "x"\nkind = "project"\nstate = "ACTIVE"\npriority = "LOW"\n', encoding="utf-8")
            result = subprocess.run([sys.executable, str(ROOT / "kit/portfolio.py"), str(first), str(second)], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("workspace directory names must be unique", result.stderr)

    def test_failed_portfolio_invalidates_old_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workspace = root / "alpha"
            workspace.mkdir()
            (workspace / "registry.toml").write_text('[[item]]\nid = "P-1"\nkind = "project"\nstate = "ACTIVE"\npriority = "LOW"\n', encoding="utf-8")
            output = root / "portfolio"
            output.mkdir()
            (output / "manifest.json").write_text('{"stale": true}\n', encoding="utf-8")
            missing = root / "missing"
            result = subprocess.run([sys.executable, str(ROOT / "kit/portfolio.py"), str(workspace), str(missing), "--output", str(output)], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((output / "manifest.json").exists())

    def test_ambiguous_source_is_not_assigned(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            registry = root / "registry.json"
            registry.write_text(json.dumps({"schema_version": 1, "items": [
                {"id": "one", "kind": "project", "state": "ACTIVE", "priority": "LOW", "source": "STATUS.md"},
                {"id": "two", "kind": "project", "state": "ACTIVE", "priority": "LOW", "source": "STATUS.md"},
            ]}), encoding="utf-8")
            observations = root / "observations.json"
            observations.write_text(json.dumps({"signals": [{"source": str(root / "STATUS.md")}, {"source": str(root / "STATUS.md")}] }), encoding="utf-8")
            result = subprocess.run([sys.executable, str(ROOT / "kit/render_context.py"), str(registry), "--observations", str(observations), "--format", "json"], check=True, capture_output=True, text=True)
            items = json.loads(result.stdout)["items"]
            self.assertEqual([item["signal_count"] for item in items], [0, 0])
            self.assertEqual({item["source_match"] for item in items}, {"ambiguous"})

    def test_same_basename_in_distinct_directories_is_not_assigned(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            registry = root / "registry.json"
            registry.write_text(json.dumps({"schema_version": 1, "items": [
                {"id": "one", "kind": "project", "state": "ACTIVE", "priority": "LOW", "source": "STATUS.md"},
            ]}), encoding="utf-8")
            observations = root / "observations.json"
            observations.write_text(json.dumps({"signals": [
                {"source": str(root / "alpha" / "STATUS.md")},
                {"source": str(root / "beta" / "STATUS.md")},
            ]}), encoding="utf-8")
            result = subprocess.run([sys.executable, str(ROOT / "kit/render_context.py"), str(registry), "--observations", str(observations), "--format", "json"], check=True, capture_output=True, text=True)
            item = json.loads(result.stdout)["items"][0]
            self.assertEqual(item["signal_count"], 0)
            self.assertEqual(item["source_match"], "ambiguous")

    def test_relative_source_path_disambiguates_same_basenames(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            registry = root / "registry.json"
            registry.write_text(json.dumps({"schema_version": 1, "items": [
                {"id": "one", "kind": "project", "state": "ACTIVE", "priority": "LOW", "source": "alpha/STATUS.md"},
                {"id": "two", "kind": "project", "state": "ACTIVE", "priority": "LOW", "source": "beta/STATUS.md"},
            ]}), encoding="utf-8")
            observations = root / "observations.json"
            observations.write_text(json.dumps({"signals": [
                {"source": str(root / "alpha" / "STATUS.md")},
                {"source": str(root / "alpha" / "STATUS.md")},
                {"source": str(root / "beta" / "STATUS.md")},
            ]}), encoding="utf-8")
            result = subprocess.run([sys.executable, str(ROOT / "kit/render_context.py"), str(registry), "--observations", str(observations), "--format", "json"], check=True, capture_output=True, text=True)
            items = json.loads(result.stdout)["items"]
            self.assertEqual([(item["id"], item["signal_count"], item["source_match"]) for item in items], [("one", 2, "unique"), ("two", 1, "unique")])

    def test_missing_source_is_explicitly_unmatched(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            registry = root / "registry.json"
            registry.write_text(json.dumps({"schema_version": 1, "items": [
                {"id": "no-source", "kind": "project", "state": "ACTIVE", "priority": "LOW"},
            ]}), encoding="utf-8")
            result = subprocess.run([sys.executable, str(ROOT / "kit/render_context.py"), str(registry), "--format", "json"], check=True, capture_output=True, text=True)
            item = json.loads(result.stdout)["items"][0]
            self.assertEqual(item["source_match"], "none")
            self.assertEqual(item["signal_count"], 0)

    def test_html_projection_escapes_declared_values(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            registry = root / "registry.json"
            registry.write_text(json.dumps({"schema_version": 1, "items": [
                {"id": "<script>alert(1)</script>", "kind": "project", "state": "ACTIVE", "priority": "HIGH"},
            ]}), encoding="utf-8")
            result = subprocess.run([sys.executable, str(ROOT / "kit/render_context.py"), str(registry), "--format", "html"], check=True, capture_output=True, text=True)
            self.assertNotIn("<script>alert(1)</script>", result.stdout)
            self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", result.stdout)

    def test_observer_does_not_follow_symlinks(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with tempfile.TemporaryDirectory() as outside_directory:
                outside = Path(outside_directory) / "outside.md"
                outside.write_text("TODO: must not be observed\n", encoding="utf-8")
                link = root / "linked.md"
                try:
                    link.symlink_to(outside)
                except (OSError, NotImplementedError):
                    self.skipTest("symbolic links are unavailable")
                result = subprocess.run([sys.executable, str(ROOT / "kit/observer.py"), str(root)], check=True, capture_output=True, text=True)
                observations = json.loads((root / "observations.json").read_text())
                self.assertEqual(observations["signals"], [])
                self.assertEqual(result.stdout.strip(), str(root / "observations.json"))

    def test_custom_marker_replaces_defaults(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "registry.toml").write_text((ROOT / "examples/minimal/registry.toml").read_text(), encoding="utf-8")
            (root / "notes.md").write_text("A REVISER signal\nTODO is deliberately ignored\n", encoding="utf-8")
            subprocess.run([sys.executable, str(ROOT / "kit/refresh.py"), str(root), "--marker", "REVISER"], check=True)
            signals = json.loads((root / "generated/observations.json").read_text())["signals"]
            self.assertEqual(len(signals), 1)
            self.assertIn("REVISER", signals[0]["signal"])
            observations = json.loads((root / "generated/observations.json").read_text())
            self.assertEqual(observations["markers"], ["REVISER"])

    def test_empty_marker_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run([sys.executable, str(ROOT / "kit/observer.py"), directory, "--marker", ""], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("value must not be empty", result.stderr)

    def test_external_output_does_not_exclude_source_corpus(self):
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as output_directory:
            root = Path(directory)
            (root / "registry.toml").write_text((ROOT / "examples/minimal/registry.toml").read_text(), encoding="utf-8")
            (root / "STATUS.md").write_text("TODO: source signal\n", encoding="utf-8")
            output = Path(output_directory) / "generated"
            subprocess.run([sys.executable, str(ROOT / "kit/refresh.py"), str(root), "--output", str(output)], check=True)
            signals = json.loads((output / "observations.json").read_text())["signals"]
            self.assertEqual(len(signals), 1)

    def test_absolute_output_is_excluded_when_source_is_relative(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "registry.toml").write_text((ROOT / "examples/minimal/registry.toml").read_text(), encoding="utf-8")
            (root / "STATUS.md").write_text("TODO: source signal\n", encoding="utf-8")
            output = root / "generated" / "observations.json"
            result = subprocess.run([sys.executable, str(ROOT / "kit/observer.py"), ".", "--output", str(output.resolve())], cwd=root, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            signals = json.loads(output.read_text())["signals"]
            self.assertEqual(len(signals), 1)

    def test_excluded_directory_is_not_observed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "registry.toml").write_text((ROOT / "examples/minimal/registry.toml").read_text(), encoding="utf-8")
            ignored = root / "node_modules"
            ignored.mkdir()
            (ignored / "dependency.md").write_text("TODO: third-party marker\n", encoding="utf-8")
            subprocess.run([sys.executable, str(ROOT / "kit/refresh.py"), str(root), "--exclude-dir", "node_modules"], check=True)
            observations = json.loads((root / "generated/observations.json").read_text())
            signals = observations["signals"]
            self.assertEqual(signals, [])
            self.assertEqual(observations["excluded_dirs"], ["node_modules"])
            self.assertIn("excluded_dirs: node_modules", (root / "generated/context.txt").read_text())
            self.assertIn("Excluded directories: node_modules", (root / "generated/context.html").read_text())

    def test_excluded_directory_does_not_match_source_ancestors(self):
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            root = parent / "workspace"
            root.mkdir()
            (root / "STATUS.md").write_text("TODO: source signal\n", encoding="utf-8")
            result = subprocess.run([sys.executable, str(ROOT / "kit/observer.py"), str(root), "--exclude-dir", parent.name], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            observations = json.loads((root / "observations.json").read_text())
            self.assertEqual(len(observations["signals"]), 1)

if __name__ == "__main__":
    unittest.main()
