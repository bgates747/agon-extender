#!/usr/bin/env python3
"""Project an HW-001 YAML electrical model into an editable KiCad schematic.

The YAML model remains electrical authority. This task-local spike supplies
only KiCad symbol choices and automated human-facing placement/routing. Never
infer product connectivity from this generator or its illustrative output.
"""

from __future__ import annotations

import argparse
import importlib.util
import os
import re
import shutil
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parent
DEFAULT_PROJECTION = ROOT / "kicad-projection.yaml"
DEFAULT_OUTPUT = ROOT / "generated"
KICAD_SYMBOLS = Path("/usr/share/kicad/symbols")


class ProjectionError(ValueError):
    """An invalid or incompatible human-view projection."""


def ensure_deterministic_python_hashes() -> None:
    """Re-exec with stable hash ordering before SKiDL builds placement sets.

    SKiDL 2.3.0 seeds its pseudo-random placer but also iterates Python sets;
    process-randomized string hashes can therefore produce a different valid
    floorplan for identical inputs. Re-executing before importing SKiDL gives
    the projection generator the deterministic ordering its seed assumes.
    """

    if os.environ.get("PYTHONHASHSEED") == "0":
        return
    environment = os.environ.copy()
    environment["PYTHONHASHSEED"] = "0"
    script = str(Path(sys.argv[0]).resolve())
    os.execve(sys.executable, [sys.executable, script, *sys.argv[1:]], environment)


def load_model_validator():
    spec = importlib.util.spec_from_file_location("hw001_model_validator", ROOT / "validate.py")
    if spec is None or spec.loader is None:
        raise ProjectionError("cannot load HW-001 electrical-model validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as stream:
        document = yaml.safe_load(stream)
    if not isinstance(document, dict):
        raise ProjectionError(f"{path}: top-level YAML value must be a mapping")
    return document


def configure_kicad_environment() -> None:
    if not KICAD_SYMBOLS.is_dir():
        raise ProjectionError(f"KiCad symbol directory is missing: {KICAD_SYMBOLS}")
    # SKiDL probes several supported KiCad generations during import. Point all
    # probes at the installed libraries so irrelevant missing-variable warnings
    # do not obscure projection errors. The selected backend remains KiCad 7.
    for variable in (
        "KICAD_SYMBOL_DIR",
        "KICAD6_SYMBOL_DIR",
        "KICAD7_SYMBOL_DIR",
        "KICAD8_SYMBOL_DIR",
        "KICAD9_SYMBOL_DIR",
        "KICAD10_SYMBOL_DIR",
    ):
        os.environ.setdefault(variable, str(KICAD_SYMBOLS))


def suppress_unsupported_kicad7_erc_probe() -> None:
    """Disable SKiDL's false ERC warning when the selected CLI lacks ERC.

    SKiDL 2.3.0 unconditionally invokes ``kicad-cli sch erc`` after writing a
    schematic. The project's installed KiCad 7.0.11 CLI has no ``sch erc``
    subcommand, so that compatibility mismatch is reported as five schematic
    warnings even though no ERC ran. Suppress only that unsupported probe; the
    subsequent KiCad load/export and exact netlist comparison remain mandatory.
    Remove this workaround when the selected KiCad CLI supplies ERC or SKiDL
    feature-detects the command itself.
    """

    executable = shutil.which("kicad-cli")
    if executable is None:
        return
    result = subprocess.run(
        [executable, "sch", "--help"],
        capture_output=True,
        text=True,
        check=False,
    )
    if "erc" in result.stdout.lower():
        return
    from skidl.tools.kicad7 import sexp_schematic

    sexp_schematic._validate_with_kicad_cli = lambda _filepath: None


def validate_projection(projection: dict[str, Any], model: dict[str, Any]) -> None:
    expected_keys = {
        "schema_version",
        "source_model",
        "tool",
        "top_name",
        "title",
        "components",
    }
    if set(projection) != expected_keys:
        raise ProjectionError(
            f"projection keys must be exactly {sorted(expected_keys)}"
        )
    if projection["schema_version"] != 1:
        raise ProjectionError("projection schema_version must be 1")
    if projection["tool"] != "kicad7":
        raise ProjectionError("this bounded spike supports only kicad7")

    mappings = projection["components"]
    if not isinstance(mappings, list):
        raise ProjectionError("projection components must be a list")
    refs = [mapping.get("ref") for mapping in mappings]
    if any(set(mapping) != {"ref", "library", "symbol"} for mapping in mappings):
        raise ProjectionError("each component mapping requires only ref, library, and symbol")
    if len(refs) != len(set(refs)):
        raise ProjectionError("projection contains duplicate component references")

    model_refs = [component["ref"] for component in model["components"]]
    if refs != model_refs:
        raise ProjectionError(
            "projection component references must exactly match canonical model order"
        )


def build_circuit(
    model: dict[str, Any],
    projection: dict[str, Any],
    projection_directory: Path,
    *,
    force_label_stubs: bool = True,
):
    configure_kicad_environment()
    # SKiDL 2.3.0 creates `skidl.log` and `skidl.erc` in the process working
    # directory as an import side effect, even though this generator requests
    # neither file. Import it inside an owned temporary directory and disable
    # its file logger before returning to the caller's directory. This is an
    # inherited-tool containment workaround, not project output handling; do
    # not delete similarly named caller files because they may predate us.
    caller_directory = Path.cwd()
    with tempfile.TemporaryDirectory(prefix="hw001-skidl-sidecars-") as scratch:
        os.chdir(scratch)
        try:
            from skidl import Circuit, KICAD7, Net, Part, lib_search_paths
            from skidl.logger import stop_log_file_output

            stop_log_file_output()
        finally:
            os.chdir(caller_directory)

    custom_library_path = str(projection_directory)
    if custom_library_path not in lib_search_paths[KICAD7]:
        lib_search_paths[KICAD7].insert(0, custom_library_path)

    circuit = Circuit(name=projection["top_name"])
    model_components = {component["ref"]: component for component in model["components"]}
    parts = {}

    for mapping in projection["components"]:
        ref = mapping["ref"]
        component = model_components[ref]
        kwargs: dict[str, Any] = {
            "tool": KICAD7,
            "circuit": circuit,
            "ref": ref,
        }
        if component.get("value"):
            kwargs["value"] = component["value"]
        part = Part(mapping["library"], mapping["symbol"], **kwargs)

        model_pins = {terminal["pin"] for terminal in component["terminals"]}
        symbol_pins = {str(pin.num) for pin in part.pins}
        if model_pins != symbol_pins:
            missing = sorted(model_pins - symbol_pins)
            extra = sorted(symbol_pins - model_pins)
            raise ProjectionError(
                f"{ref}: model/symbol pin mismatch; missing={missing}, extra={extra}"
            )
        parts[ref] = part

    for net_record in model["nets"]:
        net = Net(net_record["net_id"], circuit=circuit)
        for member in net_record["members"]:
            net += parts[member["component"]][member["pin"]]
        if force_label_stubs:
            # The primary projection deliberately uses named labels at every
            # endpoint. Marking stubs explicitly preserves every canonical
            # net_id, including two-terminal nets that SKiDL otherwise snaps
            # into anonymous wires. Experimental callers may leave nets
            # unstubbed so SKiDL can place, classify, and route them itself.
            net._stub = True
            net._stub_explicit = True
            for pin in net.get_pins():
                pin.stub = True

    for endpoint in model["unconnected"]:
        circuit.NC += parts[endpoint["component"]][endpoint["pin"]]

    return circuit


def downgrade_skidl_output_for_kicad7(path: Path) -> None:
    """Remove KiCad-8-era fields emitted by SKiDL's KiCad 7 backend.

    SKiDL 2.3.0 routes `tool="kicad7"` through a writer that identifies its
    output as schematic format 20230409 and emits `generator_version`,
    `exclude_from_sim`, and `embedded_fonts`. KiCad 7.0.11 rejects that file.
    The documented KiCad 7 format used by this workstation is 20230121.

    This is an inherited-tool workaround, not an Extender file-format fork.
    It must be removed when SKiDL emits a file accepted by the selected KiCad
    baseline or when HW-001 selects a different projection generator. The
    subsequent `kicad-cli` load/export and normalized-netlist comparison are
    mandatory proof that the downgraded projection remains valid and exact.
    """

    text = path.read_text(encoding="utf-8")
    if "(version 20230409)" not in text:
        raise ProjectionError(
            f"{path}: expected SKiDL schematic version 20230409 for bounded downgrade"
        )
    text = text.replace("(version 20230409)", "(version 20230121)", 1)
    text = text.replace('(generator "skidl")', "(generator skidl)", 1)
    text = re.sub(r"^\s*\(generator_version \"[^\"]*\"\)\n", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*\(exclude_from_sim (?:yes|no)\)\n", "", text, flags=re.MULTILINE)
    text = re.sub(
        r"\(pin_numbers\s+\(hide yes\)\)",
        "(pin_numbers hide)",
        text,
    )
    text = re.sub(
        r"\(pin_names\s+(\(offset [^)]+\))\s+\(hide yes\)\)",
        r"(pin_names \1 hide)",
        text,
    )
    text = text.replace("(fields_autoplaced yes)", "(fields_autoplaced)")
    text = text.replace("(hide yes)", "hide")

    # Generic connector symbols arrive with Pin_N names shown and immutable
    # pin numbers hidden. Named-net stubs make the former redundant and prone
    # to overlap; reverse only those display flags. Discover the connector
    # types actually embedded in this projection rather than coupling this
    # reusable generator to the original two- and three-pin demonstration.
    connector_symbols = sorted(
        set(
            re.findall(
                r'^    \(symbol "(Connector_Generic:[^"]+)"',
                text,
                flags=re.MULTILINE,
            )
        )
    )
    for connector_symbol in connector_symbols:
        pattern = re.compile(
            rf'(^    \(symbol "{re.escape(connector_symbol)}".*?)(?=^    \(symbol "|^  \)\n)',
            flags=re.MULTILINE | re.DOTALL,
        )
        match = pattern.search(text)
        if match is None:
            raise ProjectionError(f"{path}: missing embedded {connector_symbol}")
        section = match.group(1)
        section = section.replace("      (pin_numbers hide)\n", "", 1)
        section = section.replace(
            "(pin_names\n        (offset 0))",
            "(pin_names\n        (offset 0)\n        hide)",
            1,
        )
        text = text[: match.start(1)] + section + text[match.end(1) :]

    root_match = re.search(
        r"^  \(uuid ([0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12})\)$",
        text,
        flags=re.MULTILINE,
    )
    if root_match is None:
        raise ProjectionError(f"{path}: expected one root schematic UUID")
    stable_root_uuid = str(
        uuid.uuid5(
            uuid.NAMESPACE_URL,
            f"https://github.com/tomm/agon-extender/hw-001/{path.stem}",
        )
    )
    text = text.replace(root_match.group(1), stable_root_uuid)

    converted_lines = []
    embedded_count = 0
    for line in text.splitlines(keepends=True):
        match = re.match(r"^(\s*)\(embedded_fonts no\)(\)*)\s*$", line)
        if match:
            embedded_count += 1
            converted_lines.append(f"{match.group(1)}{match.group(2)}\n")
        else:
            converted_lines.append(line)
    if embedded_count == 0:
        raise ProjectionError(f"{path}: expected embedded_fonts fields were absent")
    path.write_text("".join(converted_lines), encoding="utf-8")


def generate(projection_path: Path, output_dir: Path, placement_seed: int) -> Path:
    projection_path = projection_path.resolve()
    projection = load_yaml(projection_path)
    model_path = (projection_path.parent / projection["source_model"]).resolve()
    validator = load_model_validator()
    model = validator.validate(model_path)
    validate_projection(projection, model)

    output_dir.mkdir(parents=True, exist_ok=True)
    circuit = build_circuit(model, projection, projection_path.parent)
    suppress_unsupported_kicad7_erc_probe()
    circuit.generate_schematic(
        tool="kicad7",
        filepath=str(output_dir),
        top_name=projection["top_name"],
        title=projection["title"],
        flatness=1.0,
        retries=4,
        # SKiDL's force-directed placer is randomized. A fixed seed makes this
        # generated review artifact stable across identical invocations.
        seed=placement_seed,
        # Explicit label stubs make every component electrically independent
        # for placement purposes. Put those floating blocks on a grid so a
        # large projection does not collapse pull networks and series parts
        # into one force-directed knot.
        grid_blocks=True,
        # SKiDL 2.3.0's full-wire router failed this seven-component graph even
        # after four expanded placement attempts. Explicit labeled stubs are
        # the deliberate projection style for this spike: they preserve exact
        # net names and membership while avoiding arbitrary crossing wires.
        auto_stub=False,
    )
    output = output_dir / f"{projection['top_name']}.kicad_sch"
    if not output.is_file():
        raise ProjectionError(f"SKiDL did not create expected schematic: {output}")
    downgrade_skidl_output_for_kicad7(output)
    return output


def main() -> int:
    ensure_deterministic_python_hashes()
    parser = argparse.ArgumentParser(
        description="Generate the illustrative HW-001 KiCad schematic projection."
    )
    parser.add_argument("--projection", type=Path, default=DEFAULT_PROJECTION)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--placement-seed",
        type=int,
        default=1,
        help="fixed SKiDL placement seed (default: 1)",
    )
    args = parser.parse_args()
    try:
        output = generate(args.projection, args.output_dir, args.placement_seed)
    except (OSError, yaml.YAMLError, ProjectionError, ValueError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print(f"PASS: generated {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
