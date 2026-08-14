"""Coverage-guided fuzz target for malformed metadata JSON input."""

from __future__ import annotations

import json
import sys

import atheris

with atheris.instrument_imports(include=["memdevice_bench"]):
    from memdevice_bench.metadata import (
        MetadataValidationError,
        metadata_from_dict,
        validate_metadata,
    )


def test_one_input(data: bytes) -> None:
    """Exercise metadata decoding and validation with arbitrary JSON."""

    try:
        payload = json.loads(data[:65_536].decode("utf-8", errors="replace"))
        if not isinstance(payload, dict):
            return
        metadata = metadata_from_dict(payload)
        validate_metadata(metadata, strict=False)
    except (
        json.JSONDecodeError,
        MetadataValidationError,
        OverflowError,
        RecursionError,
        TypeError,
        ValueError,
    ):
        return


def main() -> None:
    atheris.Setup(sys.argv, test_one_input)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
