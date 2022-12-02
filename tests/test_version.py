"""Test for versions."""
import json

import pytest

from custom_components.knmi.const import VERSION


@pytest.mark.asyncio
async def test_component_version():
    """Verify that the version in the manifest and const.py are equal"""
    with open(
        file="custom_components/knmi/manifest.json", mode="r", encoding="UTF-8"
    ) as manifest_file:
        data = manifest_file.read()

    manifest = json.loads(data)
    assert manifest["version"] == VERSION
