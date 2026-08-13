"""Coverage-guided fuzz target for malformed pulse-update CSV input."""

from __future__ import annotations

import io
import sys

import atheris

with atheris.instrument_imports(include=["memdevice_bench"]):
    import pandas as pd

    from memdevice_bench.schema import validate_trace


def test_one_input(data: bytes) -> None:
    """Exercise schema validation with a bounded, arbitrarily malformed CSV."""

    try:
        trace = pd.read_csv(
            io.StringIO(data[:65_536].decode("utf-8", errors="replace")),
            on_bad_lines="skip",
            nrows=256,
        )
    except (pd.errors.EmptyDataError, pd.errors.ParserError, UnicodeError):
        return

    validate_trace(trace, strict=False)


def main() -> None:
    atheris.Setup(sys.argv, test_one_input)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
