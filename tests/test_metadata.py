"""Test for metadata."""

import json
import re
import tomllib
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


def get_dependency_version(dependencies: list[str], package: str) -> str | None:
    """Extract the version of a specific package from a list of dependencies."""
    pattern = re.compile(rf"^{re.escape(package)}==(.+)$")
    for dep in dependencies:
        match = pattern.match(dep)
        if match:
            return match.group(1)
    return None


def test_versions_match() -> None:
    """Verify that the version of the library in pyproject.toml matches the one in manifest.json."""
    lib = "weerlive-api"

    # Load pyproject.toml
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    with pyproject_path.open("rb") as f:
        pyproject = tomllib.load(f)

    pyproject_deps = pyproject.get("project", {}).get("dependencies", [])
    assert pyproject_deps != []
    pyproject_version = get_dependency_version(pyproject_deps, lib)

    # Load manifest.json
    manifest_path = Path(__file__).parent.parent / "custom_components" / "knmi" / "manifest.json"
    with manifest_path.open() as f:
        manifest = json.load(f)

    manifest_deps = manifest.get("requirements", [])
    assert manifest_deps != []
    manifest_version = get_dependency_version(manifest_deps, lib)

    assert manifest_version == pyproject_version, (
        f"Version mismatch: manifest.json has {lib}=={manifest_version}, but pyproject.toml has {lib}=={pyproject_version}"
    )
