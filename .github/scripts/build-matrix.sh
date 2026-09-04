#!/usr/bin/env bash

set -euo pipefail

if (( $# > 1 )); then
  echo "usage: $0 [base-commit]" >&2
  exit 2
fi

base_commit="${1:-}"

all_contexts() {
  for context in ci/*; do
    [[ -d "$context" ]] && printf '%s\n' "$context"
  done
  return 0
}

changed_contexts() {
  if [[ -z "$base_commit" || "$base_commit" == 0000000000000000000000000000000000000000 ]] \
    || ! git cat-file -e "${base_commit}^{commit}" 2>/dev/null \
    || ! git merge-base --is-ancestor "$base_commit" HEAD; then
    all_contexts
    return
  fi

  local changed_files file
  changed_files=$(git log --format= --name-only --no-renames -m "${base_commit}..HEAD")

  while IFS= read -r file; do
    case "$file" in
      .github/workflows/publish.yml|.github/scripts/*)
        all_contexts
        return
        ;;
    esac
  done <<< "$changed_files"

  while IFS= read -r file; do
    if [[ "$file" == ci/*/* ]]; then
      file="${file#ci/}"
      printf 'ci/%s\n' "${file%%/*}"
    fi
  done <<< "$changed_files"
}

contexts=$(changed_contexts | sort -u)

while IFS= read -r context; do
  [[ -d "$context" ]] || continue

  if [[ ! "$context" =~ ^ci/[a-z0-9]+(-[a-z0-9]+)*$ ]]; then
    echo "invalid image directory: $context" >&2
    exit 1
  fi

  if [[ ! -f "$context/Dockerfile" || ! -f "$context/variants.yaml" ]]; then
    echo "$context must contain Dockerfile and variants.yaml" >&2
    exit 1
  fi

  yq -o=json '.' "$context/variants.yaml" | jq -ce --arg context "$context" '
    def single_line:
      type == "string" and (test("[\\r\\n]") | not);

    # Leave 45 characters for the -sha-<40-character commit> suffix.
    def image_tag:
      single_line and test("^[A-Za-z0-9_][A-Za-z0-9_.-]{0,82}$");

    if (
      .schema == 1
      and (.description | single_line and length > 0 and length <= 512)
      and (.variants | type == "array" and length > 0)
      and all(.variants[];
        (.tag | image_tag)
        and (.build_args | type == "object")
        and all(.build_args | to_entries[];
          (.key | test("^[A-Za-z_][A-Za-z0-9_]*$"))
          and (.value | single_line)
        )
      )
      and (([.variants[].tag] | unique | length) == (.variants | length))
    )
    then . as $manifest | .variants[] | {
      image: $context,
      context: $context,
      description: $manifest.description,
      tag,
      build_args: (.build_args | to_entries | map("\(.key)=\(.value)") | join("\n"))
    }
    else error("invalid image contract: \($context)")
    end
  '
done <<< "$contexts" | jq -sc '.'
