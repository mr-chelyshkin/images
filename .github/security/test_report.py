import json
from pathlib import Path
import tempfile
import unittest

from report import summarize


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.matrix = [dict(id=str(i), image=f"ghcr.io/example/image{i}",
                            tag="1.0", platform="linux/amd64") for i in range(2)]

    def write_report(self, index, severity=None, suppressed=False):
        item = self.matrix[index]
        folder = self.directory / f"trivy-{item['id']}"
        folder.mkdir()
        result = dict(item, status="success", digest="sha256:" + "a" * 64,
                      completed_at="2026-09-06T00:00:00+00:00")
        (folder / "result.json").write_text(json.dumps(result))
        target = {}
        if severity:
            finding = dict(Severity=severity, VulnerabilityID="CVE-example", PkgName="example")
            if suppressed:
                target["ExperimentalModifiedFindings"] = [dict(
                    Type="vulnerability", Status="ignored", Finding=finding,
                    Statement="Accepted until upstream fix | review <soon>")]
            else:
                target["Vulnerabilities"] = [finding]
        (folder / "report.json").write_text(json.dumps(dict(SchemaVersion=2, Results=[target])))

    def summarize(self, upstream="success"):
        return summarize(self.matrix, self.directory, {"HIGH", "CRITICAL"}, upstream)

    def test_reports_every_image_after_first_policy_failure(self):
        self.write_report(0, "CRITICAL")
        self.write_report(1, "LOW")
        report, failed = self.summarize()
        self.assertTrue(failed)
        self.assertIn("image0:1.0 | linux/amd64 | FAIL", report)
        self.assertIn("image1:1.0 | linux/amd64 | PASS", report)

    def test_missing_report_cannot_pass(self):
        self.write_report(1)
        report, failed = self.summarize()
        self.assertTrue(failed)
        self.assertIn("image0:1.0 | linux/amd64 | ERROR", report)
        self.assertIn("image1:1.0 | linux/amd64 | PASS", report)

    def test_ignored_findings_stay_visible_without_failing(self):
        self.write_report(0, "CRITICAL", suppressed=True)
        self.write_report(1, "MEDIUM")
        report, failed = self.summarize()
        self.assertFalse(failed)
        self.assertIn("CVE-example", report)
        self.assertIn("Accepted until upstream fix &#124; review &lt;soon&gt;", report)

    def test_upstream_failure_cannot_pass_with_all_reports(self):
        self.write_report(0)
        self.write_report(1)
        self.assertTrue(self.summarize("failure")[1])

    def test_wrong_target_and_malformed_report_cannot_pass(self):
        self.write_report(0)
        self.write_report(1)
        metadata = self.directory / "trivy-0/result.json"
        result = json.loads(metadata.read_text())
        result["platform"] = "linux/arm64"
        metadata.write_text(json.dumps(result))
        (self.directory / "trivy-1/report.json").write_text("{}")
        report, failed = self.summarize()
        self.assertTrue(failed)
        self.assertEqual(report.count("| ERROR |"), 2)

    def test_empty_inventory_fails(self):
        with self.assertRaises(ValueError):
            summarize([], self.directory, {"HIGH"}, "success")


if __name__ == "__main__":
    unittest.main()
