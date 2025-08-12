# Home Assistant Configuration

This folder is used as the configuration directory for Home Assistant when running in a development container or GitHub Codespace.

## Why is this folder in the repo?

When Home Assistant is started in the development environment, it uses this directory for all its configuration files, logs, and other runtime data. Keeping it in the repository ensures a consistent setup for development.

## Git Ignore Policy

This folder is ignored by Git to prevent committing personal data, logs, and temporary files. However, some essential configuration files, like `configuration.yaml`, are included to provide a working base configuration.
