#!/bin/bash
# Update skills sourced from anthropics/skills upstream repo.
# Usage: ./update-upstream.sh [skill-name]
#   No args: update all upstream skills
#   With arg: update only the specified skill

set -e

REPO="https://raw.githubusercontent.com/anthropics/skills/main/skills"
SKILLS_DIR="$(cd "$(dirname "$0")" && pwd)"

# Map of skill-name -> list of files to download (relative to upstream skill dir)
declare -A SKILL_FILES
SKILL_FILES["skill-creator"]="
SKILL.md
LICENSE.txt
agents/analyzer.md
agents/comparator.md
agents/grader.md
references/schemas.md
scripts/__init__.py
scripts/aggregate_benchmark.py
scripts/generate_report.py
scripts/improve_description.py
scripts/package_skill.py
scripts/quick_validate.py
scripts/run_eval.py
scripts/run_loop.py
scripts/utils.py
eval-viewer/generate_review.py
eval-viewer/viewer.html
assets/eval_review.html
"

update_skill() {
    local skill="$1"
    local files="${SKILL_FILES[$skill]}"

    if [[ -z "$files" ]]; then
        echo "Unknown skill: $skill"
        return 1
    fi

    echo "Updating $skill..."
    local target="$SKILLS_DIR/$skill"

    while IFS= read -r file; do
        [[ -z "$file" ]] && continue
        local dir
        dir="$(dirname "$file")"
        mkdir -p "$target/$dir"
        curl -fsSL "$REPO/$skill/$file" -o "$target/$file"
        echo "  $file"
    done <<< "$files"

    echo "Done: $skill"
}

if [[ -n "$1" ]]; then
    update_skill "$1"
else
    for skill in "${!SKILL_FILES[@]}"; do
        update_skill "$skill"
    done
fi
