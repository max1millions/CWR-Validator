# -*- coding: utf-8 -*-

from __future__ import annotations

from cwr_validator.preprocess import normalize_contents_for_decode


def test_hdr_ipnn_workaround_rewrites_sender_type():
    hdr = (
        "HDR01278837007RIGHTSTUNE                                   "
        "01.102026062910551820260629ASCII          2.2\r\n"
        "GRHNWR0000102.200000000001\r\n"
    )
    result = normalize_contents_for_decode(hdr, "2.2")
    assert result.startswith("HDRPB278837007RIGHTSTUNE")
    assert "GRHNWR0000102.100000000001" in result


def test_hdr_standard_sender_type_unchanged():
    hdr = "HDRPB226144593AGENCIA GRUPO MUSICAL                        01.102013080902591120130809\r\n"
    assert normalize_contents_for_decode(hdr, "2.1") == hdr
