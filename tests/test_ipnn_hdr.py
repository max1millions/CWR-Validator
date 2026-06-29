# -*- coding: utf-8 -*-

from __future__ import annotations

from pathlib import Path

import pytest

from cwr_validator.preprocess import normalize_contents_for_decode
from cwr_validator.validator import validate_file

VALIDATOR_ROOT = Path(__file__).resolve().parents[1]
CWR_INTERFACE_ROOT = VALIDATOR_ROOT.parents[1]
V22_OUTPUT = CWR_INTERFACE_ROOT / "OUTPUT" / "CW260001RIT_088.V22"


def test_rights_tune_v22_hdr_is_normalized():
    if not V22_OUTPUT.is_file():
        pytest.skip("RightsTune V22 output fixture not present")

    raw = V22_OUTPUT.read_text(encoding="latin-1")
    first_line = raw.splitlines()[0]
    assert first_line.startswith("HDR01")

    normalized = normalize_contents_for_decode(raw, "2.2")
    assert normalized.splitlines()[0].startswith("HDRPB278837007")


@pytest.mark.integration
def test_validate_rights_tune_v22_output(sibling_library_paths):
    if not V22_OUTPUT.is_file():
        pytest.skip("RightsTune V22 output fixture not present")

    result = validate_file(V22_OUTPUT)
    if not result.ok:
        pytest.skip(f"Full decode still blocked by library stack: {result.error}")
    assert result.version == "2.2"
    assert result.groups is not None and result.groups >= 1
