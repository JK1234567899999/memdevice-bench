"""Command-line interface."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path

from .device_profiles import (
    available_device_profiles,
    device_profiles_as_dict,
    metadata_for_device_profile,
)
from .io import load_trace, save_trace
from .metadata import (
    DatasetMetadata,
    DeviceMetadata,
    ExperimentMetadata,
    MetadataValidationError,
    load_metadata,
    save_metadata,
    validate_metadata,
)
from .report import write_report
from .schema import DataValidationError, validate_trace
from .synthetic import available_presets, generate_synthetic_trace, metadata_for_preset
from .taxonomy import vocabulary_as_dict


def _add_metadata_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--metadata",
        type=Path,
        help="JSON sidecar containing terminal count and controlled device tags",
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="memdevice-bench",
        description=(
            "Validate and benchmark pulse-update data from tagged 2-, 3-, and "
            "4-terminal memory/adaptive devices."
        ),
    )
    parser.add_argument("--version", action="version", version="memdevice-bench 0.2.0")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="validate a canonical CSV trace")
    validate.add_argument("input", type=Path)
    _add_metadata_argument(validate)

    validate_metadata_parser = subparsers.add_parser(
        "validate-metadata", help="validate a JSON device/dataset metadata sidecar"
    )
    validate_metadata_parser.add_argument("input", type=Path)

    analyze = subparsers.add_parser("analyze", help="write a complete pulse-update report")
    analyze.add_argument("input", type=Path)
    analyze.add_argument("--output-dir", type=Path, required=True)
    _add_metadata_argument(analyze)

    generate = subparsers.add_parser("generate", help="generate a synthetic tagged example")
    generate.add_argument("--output", type=Path, required=True)
    generate.add_argument("--preset", choices=available_presets(), default="rram-2t")
    generate.add_argument("--device-id", default="synthetic-001")
    generate.add_argument("--cycles", type=int, default=3)
    generate.add_argument("--pulses", type=int, default=64)
    generate.add_argument("--seed", type=int, default=7)
    metadata_group = generate.add_mutually_exclusive_group()
    metadata_group.add_argument("--metadata-output", type=Path)
    metadata_group.add_argument("--no-metadata", action="store_true")

    initialize = subparsers.add_parser(
        "init-metadata", help="create a normalized metadata sidecar from tags"
    )
    initialize.add_argument("--output", type=Path, required=True)
    initialize.add_argument("--device-id", required=True)
    initialize.add_argument(
        "--template",
        choices=available_device_profiles(),
        help="start from an illustrative device-tag profile and optionally add tags",
    )
    initialize.add_argument("--terminals", type=int)
    initialize.add_argument("--technology", nargs="*", default=[])
    initialize.add_argument("--platform", nargs="*", default=[])
    initialize.add_argument("--mechanism", nargs="*", default=[])
    initialize.add_argument("--material", nargs="*", default=[])
    initialize.add_argument("--behavior", nargs="*", default=[])
    initialize.add_argument("--tag", dest="custom_tags", nargs="*", default=[])
    initialize.add_argument("--profile", default="pulse-update")
    initialize.add_argument("--instrument", default="")
    initialize.add_argument("--temperature-k", type=float)
    initialize.add_argument("--notes", default="")

    subparsers.add_parser("taxonomy", help="print the controlled tag vocabulary as JSON")
    subparsers.add_parser(
        "device-profiles", help="print illustrative multi-axis tag templates as JSON"
    )
    subparsers.add_parser("presets", help="list synthetic tutorial presets")
    return parser


def _load_optional_metadata(path: Path | None) -> DatasetMetadata | None:
    return None if path is None else load_metadata(path, strict=True)


def _run_validate(path: Path, metadata_path: Path | None) -> int:
    trace = load_trace(path, strict=False)
    report = validate_trace(trace, strict=False)
    payload: dict[str, object] = {
        "valid": report.valid,
        "errors": report.errors,
        "warnings": report.warnings,
        "rows": report.row_count,
        "devices": report.device_count,
        "device_cycles": report.cycle_count,
    }
    if metadata_path is not None:
        metadata = load_metadata(metadata_path, strict=False)
        metadata_report = validate_metadata(metadata, strict=False)
        payload["metadata_valid"] = metadata_report.valid
        payload["metadata_errors"] = metadata_report.errors
        payload["metadata_warnings"] = metadata_report.warnings
        payload["valid"] = bool(report.valid and metadata_report.valid)
    print(json.dumps(payload, indent=2))
    return 0 if payload["valid"] else 2


def _run_validate_metadata(path: Path) -> int:
    metadata = load_metadata(path, strict=False)
    report = validate_metadata(metadata, strict=False)
    payload = {
        "valid": report.valid,
        "errors": report.errors,
        "warnings": report.warnings,
        "device_id": metadata.device.device_id,
        "terminal_count": metadata.device.terminal_count,
        "technology_tags": metadata.device.technology_tags,
        "platform_tags": metadata.device.platform_tags,
    }
    print(json.dumps(payload, indent=2))
    return 0 if report.valid else 2


def _run_analyze(path: Path, output_dir: Path, metadata_path: Path | None) -> int:
    trace = load_trace(path, strict=True)
    metadata = _load_optional_metadata(metadata_path)
    report = write_report(trace, output_dir, metadata=metadata)
    print(json.dumps(report.summary, indent=2, sort_keys=True))
    print(f"Report written to {output_dir}")
    return 0


def _run_generate(
    output: Path,
    preset: str,
    device_id: str,
    cycles: int,
    pulses: int,
    seed: int,
    metadata_output: Path | None,
    no_metadata: bool,
) -> int:
    trace = generate_synthetic_trace(
        preset=preset,
        device_id=device_id,
        cycles=cycles,
        pulses_per_branch=pulses,
        seed=seed,
    )
    save_trace(trace, output)
    print(f"Synthetic trace written to {output}")
    if not no_metadata:
        destination = metadata_output or output.with_suffix(".metadata.json")
        save_metadata(metadata_for_preset(preset, device_id=device_id), destination)
        print(f"Tagged metadata written to {destination}")
    return 0


def _run_init_metadata(args: argparse.Namespace) -> int:
    if args.template is not None:
        base = metadata_for_device_profile(
            args.template,
            device_id=args.device_id,
            instrument=args.instrument,
            experiment_profile=args.profile,
            notes=args.notes,
        )
        if args.terminals is not None and args.terminals != base.device.terminal_count:
            raise ValueError(
                f"--terminals={args.terminals} conflicts with template "
                f"{args.template!r} ({base.device.terminal_count} terminals)"
            )
        metadata = DatasetMetadata(
            device=DeviceMetadata(
                device_id=base.device.device_id,
                terminal_count=base.device.terminal_count,
                technology_tags=tuple(
                    sorted({*base.device.technology_tags, *args.technology})
                ),
                platform_tags=tuple(sorted({*base.device.platform_tags, *args.platform})),
                mechanism_tags=tuple(
                    sorted({*base.device.mechanism_tags, *args.mechanism})
                ),
                material_tags=tuple(sorted({*base.device.material_tags, *args.material})),
                behavior_tags=tuple(sorted({*base.device.behavior_tags, *args.behavior})),
                custom_tags=tuple(sorted({*base.device.custom_tags, *args.custom_tags})),
                notes=base.device.notes,
            ),
            experiment=ExperimentMetadata(
                profile=args.profile,
                instrument=args.instrument,
                temperature_k=args.temperature_k,
            ),
        )
    else:
        if args.terminals is None:
            raise ValueError("--terminals is required when --template is not used")
        if not args.technology:
            raise ValueError("--technology is required when --template is not used")
        metadata = DatasetMetadata(
            device=DeviceMetadata(
                device_id=args.device_id,
                terminal_count=args.terminals,
                technology_tags=tuple(args.technology),
                platform_tags=tuple(args.platform),
                mechanism_tags=tuple(args.mechanism),
                material_tags=tuple(args.material),
                behavior_tags=tuple(args.behavior),
                custom_tags=tuple(args.custom_tags),
                notes=args.notes,
            ),
            experiment=ExperimentMetadata(
                profile=args.profile,
                instrument=args.instrument,
                temperature_k=args.temperature_k,
            ),
        )
    save_metadata(metadata, args.output)
    print(f"Metadata written to {args.output}")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """Run the command-line interface."""

    args = _parser().parse_args(argv)
    try:
        if args.command == "validate":
            return _run_validate(args.input, args.metadata)
        if args.command == "validate-metadata":
            return _run_validate_metadata(args.input)
        if args.command == "analyze":
            return _run_analyze(args.input, args.output_dir, args.metadata)
        if args.command == "generate":
            return _run_generate(
                args.output,
                args.preset,
                args.device_id,
                args.cycles,
                args.pulses,
                args.seed,
                args.metadata_output,
                args.no_metadata,
            )
        if args.command == "init-metadata":
            return _run_init_metadata(args)
        if args.command == "taxonomy":
            print(json.dumps(vocabulary_as_dict(), indent=2, sort_keys=True))
            return 0
        if args.command == "device-profiles":
            print(json.dumps(device_profiles_as_dict(), indent=2, sort_keys=True))
            return 0
        if args.command == "presets":
            print("\n".join(available_presets()))
            return 0
    except (
        DataValidationError,
        MetadataValidationError,
        FileNotFoundError,
        ValueError,
    ) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
