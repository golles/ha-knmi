#!/usr/bin/env bash

# This script parses the CI workflow checks job from .github/workflows/ci.yaml and runs them locally. It extracts each check's name and command from
# the job matrix and executes the commands sequentially, logging the name of each check before running it.

set -e

# shellcheck source=/dev/null
source "$(dirname "$0")/utils.sh"

# Ensure required commands are installed
command_exists jq yq

cd "$(dirname "$0")/.."

# Extract names and commands using yq and convert to JSON.
entries=$(yq -o=json '.jobs.checks.strategy.matrix.include' .github/workflows/ci.yaml)

# Iterate over each entry and execute the corresponding command.
echo "$entries" | jq -c '.[]' | while IFS= read -r entry; do
  name=$(echo "$entry" | jq -r '.name')
  command=$(echo "$entry" | jq -r '.command')

  log_yellow "Run $name"
  eval "$command"
  log_empty_line 1
done
