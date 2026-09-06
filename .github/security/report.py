#!/usr/bin/env python3
"""Combine all expected Trivy reports before deciding the workflow result."""

import argparse
from collections import Counter
import html
import json
from pathlib import Path
import sys

SEVERITIES = ("CRITICAL", "HIGH", "MEDIUM", "LOW", "UNKNOWN")


def cell(value):
    return html.escape(str(value)).replace("|", "&#124;").replace("\n", " ")


def summarize(matrix, directory, severities, upstream):
    if not isinstance(matrix, list) or not matrix:
        raise ValueError("Image inventory is missing or empty")
    ids = [item["id"] for item in matrix]
    if len(set(ids)) != len(ids):
        raise ValueError("Image inventory contains duplicate IDs")

    failed = upstream != "success"
    lines = ["# Published image vulnerability scan", "",
             f"Failure threshold: {', '.join(sorted(severities))}; unfixed CVEs included.",
             "Accepted exceptions remain visible and do not count toward the threshold.", "",
             "| Image | Platform | Result | Critical | High | Medium | Low | Unknown | Ignored |",
             "|---|---|---|---:|---:|---:|---:|---:|---:|"]
    details = []
    for item in matrix:
        name = f"{item['image']}:{item['tag']}"
        folder = directory / f"trivy-{item['id']}"
        counts = Counter()
        ignored = []
        status = "ERROR"
        detail = [f"## {cell(name)} ({cell(item['platform'])})", ""]
        try:
            result = json.loads((folder / "result.json").read_text())
            if not isinstance(result, dict):
                raise ValueError("Invalid scan metadata")
            if any(result[key] != item[key] for key in ("image", "tag", "platform")):
                raise ValueError("Report does not match the expected image/tag/platform")
            if result["status"] != "success":
                raise ValueError(result.get("error") or "Scan did not complete")
            report = json.loads((folder / "report.json").read_text())
            if not isinstance(report, dict) or report.get("SchemaVersion") != 2 or not report.get("Results"):
                raise ValueError("Trivy report is incomplete or has an unsupported schema")
            for target in report["Results"]:
                if not isinstance(target, dict):
                    raise ValueError("Invalid Trivy scan target")
                for finding in target.get("Vulnerabilities") or []:
                    severity = finding["Severity"]
                    if severity not in SEVERITIES:
                        raise ValueError(f"Unsupported severity: {severity}")
                    counts[severity] += 1
                for modified in target.get("ExperimentalModifiedFindings") or []:
                    if modified["Type"] != "vulnerability" or modified["Status"] != "ignored":
                        raise ValueError("Unsupported suppressed finding schema")
                    ignored.append(modified)
            status = "FAIL" if any(counts[s] for s in severities) else "PASS"
            failed |= status == "FAIL"
            detail.extend([
                f"Digest: `{cell(result['digest'])}`  ",
                f"Scanned: {cell(result['completed_at'])}  ",
                f"Artifact: `trivy-{cell(item['id'])}` (full JSON, text report, metadata and log)", "",
            ])
            if ignored:
                detail.extend(["Accepted exceptions:", "",
                               "| CVE | Package | Installed | Fixed | Severity | Reason |",
                               "|---|---|---|---|---|---|"])
                for modified in ignored:
                    finding = modified["Finding"]
                    detail.append("| " + " | ".join(cell(v) for v in (
                        finding["VulnerabilityID"], finding["PkgName"],
                        finding.get("InstalledVersion", ""), finding.get("FixedVersion") or "unavailable",
                        finding["Severity"], modified.get("Statement", ""))) + " |")
                detail.append("")
        except (OSError, ValueError, KeyError, TypeError) as error:
            failed = True
            status = "ERROR"
            detail.extend([f"**Scan error:** {cell(error)}", ""])
        lines.append("| " + " | ".join(cell(v) for v in (
            name, item["platform"], status,
            *(counts[s] if status != "ERROR" else "—" for s in SEVERITIES),
            len(ignored) if status != "ERROR" else "—")) + " |")
        details.extend(detail)

    lines.extend(["", f"Overall result: **{'FAIL' if failed else 'PASS'}**.", ""])
    if upstream != "success":
        lines.extend([f"Scan jobs did not all succeed: {cell(upstream)}.", ""])
    lines.extend(["PASS means no findings above the configured threshold after exceptions;",
                  "it does not mean that an image has no vulnerabilities.", "", *details])
    return "\n".join(lines) + "\n", failed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix", type=Path, required=True)
    parser.add_argument("--reports", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--severity", required=True)
    parser.add_argument("--upstream", required=True)
    args = parser.parse_args()
    try:
        severities = set(args.severity.split(","))
        if not severities or not severities <= set(SEVERITIES):
            raise ValueError("Invalid failure severity threshold")
        text, failed = summarize(json.loads(args.matrix.read_text()), args.reports,
                                 severities, args.upstream)
    except (OSError, ValueError, KeyError, TypeError) as error:
        text = f"# Published image vulnerability scan\n\n**FAIL:** {cell(error)}\n"
        failed = True
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(text)
    print(text)
    return int(failed)


if __name__ == "__main__":
    sys.exit(main())
