import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch


spec = importlib.util.spec_from_file_location("scan", Path(__file__).with_name("scan.py"))
scan = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scan)

DIGEST = "sha256:" + "a" * 64
IMAGE = "ghcr.io/mr-chelyshkin/ci/rust"


def descriptor(architecture, digest=DIGEST, operating_system="linux"):
    return {
        "mediaType": "application/vnd.oci.image.manifest.v1+json",
        "digest": digest,
        "platform": {"os": operating_system, "architecture": architecture},
    }


def index(*manifests):
    return {"schemaVersion": 2, "manifests": list(manifests)}


def report():
    return {
        "SchemaVersion": 2,
        "ArtifactType": "container_image",
        "Metadata": {"ImageConfig": {"architecture": "amd64", "os": "linux"}},
        "Results": [{
            "Target": "debian 13",
            "Class": "os-pkgs",
            "Vulnerabilities": [{"VulnerabilityID": "CVE-test", "Severity": "CRITICAL"}],
        }],
    }


class ResolveTests(unittest.TestCase):
    def test_selects_architecture_and_ignores_attestations(self):
        manifest = index(descriptor("arm64", "sha256:" + "b" * 64), descriptor("amd64"),
                         descriptor("unknown", operating_system="unknown"))
        self.assertEqual(scan.resolve_digest(manifest, "linux/amd64"), DIGEST)

    def test_missing_or_ambiguous_platform_fails(self):
        for manifests in ([], [descriptor("arm64")], [descriptor("amd64"), descriptor("amd64")]):
            with self.subTest(manifests=manifests), self.assertRaises(scan.ScanError):
                scan.resolve_digest(index(*manifests), "linux/amd64")

    def test_invalid_digest_or_non_index_fails(self):
        for manifest in (index(descriptor("amd64", "sha256:bad")), {}, {"schemaVersion": 2}):
            with self.subTest(manifest=manifest), self.assertRaises(scan.ScanError):
                scan.resolve_digest(manifest, "linux/amd64")


class ScanTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.output = self.root / "output"
        self.ignore = self.root / ".trivyignore.yaml"
        self.ignore.write_text("vulnerabilities: []\n", encoding="utf-8")
        self.commands = []
        self.scan_report = report()
        self.failure = None
        self.version = {
            "Version": "test-version",
            "VulnerabilityDB": {"Version": 2, "UpdatedAt": "2026-09-06T00:00:00Z"},
        }

    def fake_run(self, command, **kwargs):
        self.commands.append(command)
        self.assertGreater(kwargs["timeout"], 0)
        if command[0] == "docker":
            stdout = json.dumps(index(descriptor("amd64")))
        elif command[1] == "image":
            if self.failure:
                return subprocess.CompletedProcess(command, 1, self.failure)
            (self.output / "report.json").write_text(json.dumps(self.scan_report), encoding="utf-8")
            stdout = "Scan completed\n"
        elif command[1] == "convert":
            (self.output / "report.txt").write_text("CVE-test CRITICAL\n", encoding="utf-8")
            stdout = ""
        else:
            stdout = json.dumps(self.version)
        return subprocess.CompletedProcess(command, 0, stdout)

    def invoke(self):
        with patch.object(scan.subprocess, "run", side_effect=self.fake_run), patch("sys.stderr", new_callable=io.StringIO):
            exit_code = scan.scan(IMAGE, "1.90.0", "linux/amd64", self.output, self.ignore)
        return exit_code, json.loads((self.output / "result.json").read_text(encoding="utf-8"))

    def test_full_scan_uses_digest_and_findings_do_not_fail(self):
        exit_code, result = self.invoke()
        self.assertEqual(exit_code, 0)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["digest"], DIGEST)
        self.assertEqual(result["trivy"]["VulnerabilityDB"]["Version"], 2)
        self.assertTrue(result["completed_at"])
        self.assertEqual((self.output / "ignore.yaml").read_text(), self.ignore.read_text())
        scan_command = self.commands[1]
        self.assertEqual(scan_command[-1], f"{IMAGE}@{DIGEST}")
        for option, value in (("--image-src", "remote"), ("--scanners", "vuln"),
                              ("--exit-code", "0"), ("--severity", scan.SEVERITIES),
                              ("--timeout", "15m")):
            self.assertEqual(scan_command[scan_command.index(option) + 1], value)
        self.assertIn("--show-suppressed", scan_command)
        self.assertIn("--ignore-unfixed=false", scan_command)
        self.assertIn("--show-suppressed", self.commands[2])

    def test_scan_error_retains_metadata_and_log(self):
        self.failure = "Cannot download image\n"
        exit_code, result = self.invoke()
        self.assertEqual(exit_code, 1)
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["digest"], DIGEST)
        self.assertIn("exited with code 1", result["error"])
        self.assertIn(self.failure, (self.output / "scan.log").read_text())
        self.assertFalse(any(command[1] == "convert" for command in self.commands))
        self.assertIsNotNone(result["trivy"])

    def test_wrong_platform_or_empty_results_are_incomplete(self):
        for mutate in (
            lambda value: value["Metadata"]["ImageConfig"].update(architecture="arm64"),
            lambda value: value.update(Results=[]),
            lambda value: value.update(SchemaVersion=3),
        ):
            with self.subTest(mutate=mutate):
                self.scan_report = report()
                mutate(self.scan_report)
                exit_code, result = self.invoke()
                self.assertEqual(exit_code, 1)
                self.assertEqual(result["status"], "error")

    def test_missing_ignore_file_retains_error_metadata(self):
        self.ignore.unlink()
        exit_code, result = self.invoke()
        self.assertEqual(exit_code, 1)
        self.assertIsNone(result["digest"])
        self.assertIsNotNone(result["trivy"])
        self.assertEqual(len(self.commands), 1)

    def test_missing_database_metadata_fails_a_completed_scan(self):
        for database in (None, {}, {"Version": 2}, {"UpdatedAt": "2026-09-06T00:00:00Z"}):
            with self.subTest(database=database):
                self.version["VulnerabilityDB"] = database
                exit_code, result = self.invoke()
                self.assertEqual(exit_code, 1)
                self.assertEqual(result["status"], "error")
                self.assertIn("database metadata is missing", result["error"])
                self.assertEqual(result["trivy"], self.version)
                self.assertTrue((self.output / "report.json").is_file())

    def test_timeout_retains_partial_log(self):
        with patch.object(scan.subprocess, "run", side_effect=subprocess.TimeoutExpired("docker", 120, output=b"Partial output\n")), patch("sys.stderr", new_callable=io.StringIO):
            exit_code = scan.scan(IMAGE, "1.90.0", "linux/amd64", self.output, self.ignore)
        self.assertEqual(exit_code, 1)
        result = json.loads((self.output / "result.json").read_text())
        self.assertIn("timed out", result["error"])
        self.assertIn("Partial output", (self.output / "scan.log").read_text())


if __name__ == "__main__":
    unittest.main()
