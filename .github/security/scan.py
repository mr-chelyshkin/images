#!/usr/bin/env python3
"""Scan one published image manifest; leave CVE policy decisions to the summary job."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys


SEVERITIES = "UNKNOWN,LOW,MEDIUM,HIGH,CRITICAL"
MANIFEST_TYPES = {
    "application/vnd.oci.image.manifest.v1+json",
    "application/vnd.docker.distribution.manifest.v2+json",
}


class ScanError(Exception):
    pass


def timestamp():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def run_command(command, log, timeout):
    log.write(f"\n$ {shlex.join(command)}\n")
    log.flush()
    try:
        process = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as error:
        output = error.output or ""
        if isinstance(output, bytes):
            output = output.decode("utf-8", errors="replace")
        log.write(output)
        log.write(f"\nTimed out after {timeout} seconds.\n")
        log.flush()
        raise ScanError(f"{command[0]} timed out after {timeout} seconds; see scan.log") from error
    log.write(process.stdout)
    log.flush()
    if process.returncode:
        raise ScanError(f"{command[0]} exited with code {process.returncode}; see scan.log")
    return process.stdout


def resolve_digest(index, platform):
    """Select a single architecture manifest, excluding BuildKit attestations."""
    if platform not in ("linux/amd64", "linux/arm64"):
        raise ScanError(f"Unsupported platform: {platform}")
    if not isinstance(index, dict) or index.get("schemaVersion") != 2:
        raise ScanError("Registry response is not a schema 2 image index")
    manifests = index.get("manifests")
    if not isinstance(manifests, list):
        raise ScanError("Tag must reference an image index with platform manifests")
    operating_system, architecture = platform.split("/")
    matches = []
    for manifest in manifests:
        if not isinstance(manifest, dict):
            raise ScanError("Registry index contains an invalid manifest descriptor")
        candidate = manifest.get("platform", {})
        if not isinstance(candidate, dict):
            raise ScanError("Registry index contains an invalid platform descriptor")
        if candidate.get("os") == operating_system and candidate.get("architecture") == architecture:
            matches.append(manifest)
    if len(matches) != 1:
        raise ScanError(f"Expected one {platform} manifest, found {len(matches)}")
    manifest = matches[0]
    digest = manifest.get("digest", "")
    if not isinstance(digest, str) or not re.fullmatch(r"sha256:[0-9a-f]{64}", digest):
        raise ScanError("Platform manifest has an invalid SHA256 digest")
    if manifest.get("mediaType") not in MANIFEST_TYPES:
        raise ScanError("Platform descriptor does not reference a supported image manifest")
    return digest


def validate_report(report, platform):
    if not isinstance(report, dict) or report.get("SchemaVersion") != 2:
        raise ScanError("Trivy report does not use the expected schema version 2")
    if report.get("ArtifactType") != "container_image":
        raise ScanError("Trivy report is not a container image scan")
    metadata = report.get("Metadata")
    config = metadata.get("ImageConfig") if isinstance(metadata, dict) else None
    operating_system, architecture = platform.split("/")
    if not isinstance(config, dict) or (config.get("os"), config.get("architecture")) != (
        operating_system, architecture
    ):
        raise ScanError(f"Trivy report does not match the requested platform {platform}")
    results = report.get("Results")
    if not isinstance(results, list) or not results or not all(isinstance(item, dict) for item in results):
        raise ScanError("Trivy report has no valid package scan targets")


def scan(image, tag, platform, output, ignorefile):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    result = {
        "image": image,
        "tag": tag,
        "platform": platform,
        "digest": None,
        "started_at": timestamp(),
        "completed_at": None,
        "status": "error",
        "error": "Scan did not complete",
        "ignorefile": str(ignorefile),
        "trivy": None,
    }
    with (output / "scan.log").open("w", encoding="utf-8") as log:
        try:
            # A repeated local invocation cannot reuse a previous successful report.
            for name in ("report.json", "report.txt", "ignore.yaml"):
                (output / name).unlink(missing_ok=True)
            shutil.copyfile(ignorefile, output / "ignore.yaml")
            raw_index = run_command(
                ["docker", "buildx", "imagetools", "inspect", "--raw", f"{image}:{tag}"],
                log, 120,
            )
            result["digest"] = resolve_digest(json.loads(raw_index), platform)
            run_command(
                [
                    "trivy", "image", "--image-src", "remote", "--scanners", "vuln",
                    "--platform", platform, "--format", "json",
                    "--output", str(output / "report.json"),
                    "--show-suppressed", "--ignorefile", str(output / "ignore.yaml"),
                    "--severity", SEVERITIES, "--ignore-unfixed=false", "--exit-code", "0",
                    "--timeout", "15m", f"{image}@{result['digest']}",
                ],
                log, 960,
            )
            with (output / "report.json").open(encoding="utf-8") as report_file:
                validate_report(json.load(report_file), platform)
            run_command(
                [
                    "trivy", "convert", "--format", "table", "--scanners", "vuln",
                    "--output", str(output / "report.txt"), "--show-suppressed",
                    "--ignorefile", str(output / "ignore.yaml"), "--severity", SEVERITIES,
                    "--exit-code", "0", str(output / "report.json"),
                ],
                log, 120,
            )
            if not (output / "report.txt").is_file() or not (output / "report.txt").stat().st_size:
                raise ScanError("Trivy did not produce the human-readable report")
            result["status"] = "success"
            result["error"] = None
        except (ScanError, OSError, ValueError) as error:
            result["error"] = str(error)
            log.write(f"\nERROR: {error}\n")
        finally:
            try:
                version = json.loads(run_command(["trivy", "--version", "--format", "json"], log, 30))
                if not isinstance(version, dict) or not isinstance(version.get("Version"), str) or not version["Version"]:
                    raise ScanError("Trivy returned invalid version metadata")
                result["trivy"] = version
                if result["status"] == "success":
                    database = version.get("VulnerabilityDB")
                    if not isinstance(database, dict) or not database.get("Version") or not database.get("UpdatedAt"):
                        raise ScanError("Trivy vulnerability database metadata is missing Version or UpdatedAt")
            except (ScanError, OSError, ValueError) as error:
                result["status"] = "error"
                result["error"] = "; ".join(filter(None, [result["error"], f"Version metadata: {error}"]))
                log.write(f"\nERROR: {error}\n")
            result["completed_at"] = timestamp()
            (output / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "success":
        print(result["error"], file=sys.stderr)
        return 1
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", required=True)
    parser.add_argument("--tag", required=True)
    parser.add_argument("--platform", required=True, choices=("linux/amd64", "linux/arm64"))
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--ignorefile", required=True, type=Path)
    args = parser.parse_args()
    return scan(args.image, args.tag, args.platform, args.output, args.ignorefile)


if __name__ == "__main__":
    sys.exit(main())
