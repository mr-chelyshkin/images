{{- define "cell" -}}{{ . | toString | escapeString | replace "|" "&#124;" | replace "\r" "" | replace "\n" " " | replace "`" "&#96;" }}{{- end -}}
{{- $critical := 0 -}}{{- $high := 0 -}}
{{- range . -}}{{- range .Vulnerabilities -}}
  {{- if eq .Severity "CRITICAL" -}}{{- $critical = add1 $critical -}}{{- end -}}
  {{- if eq .Severity "HIGH" -}}{{- $high = add1 $high -}}{{- end -}}
{{- end -}}{{- end }}
| CRITICAL | HIGH |
| ---: | ---: |
| {{ $critical }} | {{ $high }} |

{{ if eq (add $critical $high) 0 -}}
No HIGH or CRITICAL vulnerabilities found.
{{ else -}}
<details>
<summary>Vulnerability details</summary>

{{ range . -}}
{{ if .Vulnerabilities -}}
#### {{ template "cell" .Target }}

| Severity | Vulnerability | Package | Installed | Fixed |
| --- | --- | --- | --- | --- |
{{ $vulnerabilities := .Vulnerabilities -}}
{{ range $severity := list "CRITICAL" "HIGH" -}}
{{ range $vulnerabilities -}}
{{ if eq .Severity $severity -}}
| {{ .Severity }} | {{ if .PrimaryURL }}<a href="{{ escapeString .PrimaryURL }}">{{ template "cell" .VulnerabilityID }}</a>{{ else }}{{ template "cell" .VulnerabilityID }}{{ end }} | {{ template "cell" .PkgName }} | {{ template "cell" .InstalledVersion }} | {{ template "cell" (.FixedVersion | default "—") }} |
{{ end -}}
{{ end -}}
{{ end }}
{{ end -}}
{{ end -}}
</details>
{{ end }}
