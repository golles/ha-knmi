#!/usr/bin/env bash

set -e

cd "$(dirname "$0")/.."

# Set the path to custom_components
## This let's us have the structure we want <root>/custom_components/integration_blueprint
## while at the same time have Home Assistant configuration inside <root>/config
## without resulting to symlinks.
export PYTHONPATH="${PYTHONPATH}:${PWD}/custom_components"

# Install dependencies needed to run Home Assistant
uv pip install hassil home_assistant_intents mutagen pymicro_vad pyspeex_noise PyTurboJPEG

# Start Home Assistant
uv run hass --config "${PWD}/config" --debug
