# Published image scans

The [Vulnerabilities workflow](../workflows/vulnerabilities.yml) runs daily at
02:17 UTC (06:17 Asia/Tbilisi). It scans the current tags in `ci/*/variants.yaml`
for `linux/amd64` and `linux/arm64`. Historical tags and commit-qualified tags
are outside this inventory. The workflow scans published GHCR content; it does
not build or publish images.

GitHub can delay scheduled runs and disables schedules in public repositories
after 60 days without repository activity. Check the last run date when relying
on a report; see [GitHub schedule behavior](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule).

Each target resolves to its platform manifest digest before scanning. Jobs run
independently with `fail-fast: false`. The final job waits for all targets and
fails for any unaccepted HIGH/CRITICAL finding, including those without an
available fix. Download errors, incomplete scans and missing reports also fail.
LOW, MEDIUM and UNKNOWN findings remain in the reports.

Open the workflow run's summary for counts, digests and accepted exceptions.
Each `trivy-<id>` artifact contains the full JSON and text reports, scan log,
applied ignore file and metadata (scan times, digest, Trivy and database versions).
Artifacts are retained for 90 days. The `vulnerability-summary` artifact also
contains the complete target inventory. A passing run means the configured
policy passed after exceptions, not that the images have no vulnerabilities.

## Handle a CVE

1. Inspect the affected package, installed/fixed versions, image digest and
   upstream advisory in the report. Check whether the vulnerable functionality
   is relevant to how the image is used.
2. Update the base image or bundled tool when a fix is available, rebuild through
   the existing publish workflow and verify the new digest in the next scan.
3. If accepting the risk temporarily, record the reason and a review deadline in
   that image/tag's ignore file. An ignore does not fix or remove the vulnerable
   package. A newly available fix does not automatically revoke an exception.
4. Review accepted exceptions when an upstream fix appears or the deadline
   approaches. Expired entries stop suppressing the CVE.

The default [`.trivyignore.yaml`](.trivyignore.yaml) is empty. To accept a CVE
for one image/tag, create this path (shared by its two architectures):

```text
.github/security/ignores/ci/<name>/<tag>/.trivyignore.yaml
```

Use a real advisory ID and the affected package's paths/PURLs from the report,
with a concrete reason and an `expired_at` date. See the
[Trivy YAML ignore reference](https://trivy.dev/docs/latest/guide/configuration/filtering/#trivyignoreyaml).
The workflow selects exactly one file: the image/tag file when present, otherwise
the empty default. Exceptions therefore do not apply to other images or tags.
Trivy's YAML ignore format and suppressed JSON findings are experimental; the
scanner version is pinned and its output is validated before policy evaluation.

Accepted findings remain in the full reports and the run summary, including
their reason. Report links and the affected digest can be used to warn consumers;
adding an ignore does not change the published image.

## Check the workflow helpers locally

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s .github/security -p 'test_*.py'
actionlint .github/workflows/vulnerabilities.yml
```
