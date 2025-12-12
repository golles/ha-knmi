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
    git config --global --add safe.directory "$(pwd)"

    # Install pre-commit when available
    if check_uv_package "pre-commit" && [ -f .pre-commit-config.yaml ]; then
        uv run pre-commit install
    fi

    # Install auto completions
    mkdir -p ~/.zfunc
    uv generate-shell-completion zsh > ~/.zfunc/_uv
    if check_uv_package "ruff"; then
        uv run ruff generate-shell-completion zsh > ~/.zfunc/_ruff
    fi
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
    log_yellow "Once all the extensions are installed, reload the window (Command Palette -> Developer: Reload Window) to make sure all extensions are activated!"
else
    log_empty_line 1
    log_yellow "Done, you might want to reload your terminal or run \"source .venv/bin/activate\" to activate the virtual environment"
fi
