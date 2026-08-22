"""Inject explicit human-readable identity into deployable diagnostics.

Unset values deliberately compile as UNVERSIONED-DO-NOT-DEPLOY. Qualification
tooling must reject that marker; ordinary compile/link investigation remains
possible without inventing a build identity.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import re


Import("env")  # type: ignore[name-defined]  # Provided by PlatformIO/SCons.

MARKER = "UNVERSIONED-DO-NOT-DEPLOY"
VALID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9.-]*$")


def validated(name: str, value: str) -> str:
    if not VALID.fullmatch(value):
        raise RuntimeError(f"{name} contains unsupported identity characters")
    return value


def environment_identity(name: str) -> str:
    value = os.environ.get(name, MARKER)
    return validated(name, value)


environment = env.subst("$PIOENV")  # type: ignore[name-defined]
project_dir = Path(env.subst("$PROJECT_DIR"))  # type: ignore[name-defined]
identity_path = project_dir / f"pio/{environment}-identity.json"
if identity_path.is_file():
    record = json.loads(identity_path.read_text(encoding="utf-8"))
    source_identity = validated("source_identity", record["source_identity"])
    artifact_status = validated("status", record["status"])
    requested_source = os.environ.get("AGON_EXTENDER_SOURCE_IDENTITY")
    if requested_source is not None and requested_source != source_identity:
        raise RuntimeError(
            "AGON_EXTENDER_SOURCE_IDENTITY does not match committed "
            f"{identity_path.relative_to(project_dir)}"
        )
else:
    source_identity = environment_identity("AGON_EXTENDER_SOURCE_IDENTITY")
    artifact_status = MARKER


env.Append(  # type: ignore[name-defined]
    CPPDEFINES=[
        ("AGON_EXTENDER_SOURCE_IDENTITY", env.StringifyMacro(source_identity)),  # type: ignore[name-defined]
        ("AGON_EXTENDER_BUILD_ID", env.StringifyMacro(environment_identity("AGON_EXTENDER_BUILD_ID"))),  # type: ignore[name-defined]
        ("AGON_EXTENDER_ARTIFACT_STATUS", env.StringifyMacro(artifact_status)),  # type: ignore[name-defined]
    ]
)
