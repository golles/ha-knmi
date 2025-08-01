"""Test for versions."""

import json
from pathlib import Path

from custom_components.knmi.const import DOMAIN, NAME


async def test_manifest_values() -> None:
    """Verify that the manifest and const.py values are equal."""
    # Load manifest.json
    manifest_path = Path(__file__).parent.parent / "custom_components" / "knmi" / "manifest.json"
    with manifest_path.open() as f:
        manifest = json.load(f)

    assert manifest.get("domain") == DOMAIN
    assert manifest.get("name") == NAME
