#!/usr/bin/env bash

set -e

# shellcheck source=/dev/null
source "$(dirname "$0")/utils.sh"

# Ensure required commands are installed
command_exists uv npm

cd "$(dirname "$0")/.."

# Error handling
error_exit() {
    log_error "An error occurred. Exiting..."
    exit 1
}

# Trap any error and execute the error_exit function
trap error_exit ERR

# Install project dependencies
uv sync

# Install npm dependencies
npm install

if [ "$CI" != "true" ]; then
    # Trust the repo
    git config --global --add safe.directory /workspaces/ha-knmi

    # Install pre-commit when available
    if [ -f .pre-commit-config.yaml ]; then
        uv run pre-commit install
    fi

    # Install auto completions
    mkdir -p ~/.zfunc
    uv generate-shell-completion zsh > ~/.zfunc/_uv
    uv run ruff generate-shell-completion zsh > ~/.zfunc/_ruff
    if command_exists gh &> /dev/null; then
        gh completion -s zsh > ~/.zfunc/_gh
    fi
    grep -qxF 'fpath+=~/.zfunc' ~/.zshrc || echo 'fpath+=~/.zfunc' >> ~/.zshrc
    grep -qxF 'autoload -Uz compinit && compinit' ~/.zshrc || echo 'autoload -Uz compinit && compinit' >> ~/.zshrc
fi

# Check for --devcontainer argument
if [ "$1" == "--devcontainer" ]; then
    log_empty_line 2
    log_yellow "The dev container is ready"
    log_yellow "Once all the extensions are installed, reload the window (CMD+P -> Developer: Reload Window) to make sure all extensions are activated!"
else
    log_empty_line 1
    log_yellow "Done, you should reload your terminal"
fi
