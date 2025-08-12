#!/usr/bin/env bash

# This file contains utility functions used in other scripts.

set -e

# Check if all given commands exist
# Usage: command_exists cmd1 cmd2 ...
# - Logs an error for each missing command.
# - Exits with status 1 if any command is missing.
command_exists() {
    local missing=()

    for cmd in "$@"; do
        if ! command -v "$cmd" >/dev/null 2>&1; then
            log_error "$cmd is not installed. Please install it manually."
            missing+=("$cmd")
        fi
    done

    # Exit if any commands were missing
    if [ "${#missing[@]}" -ne 0 ]; then
        exit 1
    fi
}

# Function to log messages in yellow color
# Usage: log_yellow [string]
log_yellow() {
    printf '\e[33m%s\e[0m\n' "$1"
}

# Function to log error messages in red color
# Usage: log_error [string]
log_error() {
    printf '\e[31m%s\e[0m\n' "$1" >&2
}

# Function to print empty lines
# Usage: log_empty [int]
log_empty_line() {
    local count="$1"
    for _ in $(seq "$count"); do
        printf '\n'
    done
}
