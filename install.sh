#!/usr/bin/env bash
# Link this repo's skills and CLAUDE.md into ~/.claude. Safe to run repeatedly.
set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
claude_dir="${HOME}/.claude"
backup_suffix=".bak-$(date +%Y%m%d)"

link_into_place() {
  local source_path="$1"
  local target_path="$2"

  if [ -L "${target_path}" ]; then
    if [ "$(readlink "${target_path}")" = "${source_path}" ]; then
      echo "ok       ${target_path}"
      return
    fi
    rm "${target_path}"
  elif [ -e "${target_path}" ]; then
    # Keep any real file or folder that is in the way instead of deleting it
    mv "${target_path}" "${target_path}${backup_suffix}"
    echo "backup   ${target_path} -> ${target_path}${backup_suffix}"
  fi
  ln -s "${source_path}" "${target_path}"
  echo "linked   ${target_path} -> ${source_path}"
}

mkdir -p "${claude_dir}/skills"
for skill_path in "${repo_dir}"/skills/*/; do
  skill_path="${skill_path%/}"
  link_into_place "${skill_path}" "${claude_dir}/skills/$(basename "${skill_path}")"
done
link_into_place "${repo_dir}/claude/CLAUDE.md" "${claude_dir}/CLAUDE.md"

for tool in uv pandoc latexmk; do
  if ! command -v "${tool}" > /dev/null; then
    echo "warning  '${tool}' not found (uv is required; pandoc/latexmk are used for checking output)"
  fi
done
