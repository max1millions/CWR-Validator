# -*- coding: utf-8 -*-
"""Normalize CWR file contents before handing them to the DataApi decoder."""

from __future__ import annotations

import re

# CWR 2.1 Rev 8 / 2.2 Rev 2: when the sender IPNN exceeds nine digits, the leading
# two digits occupy HDR Sender Type (positions 4-5) and the remaining nine occupy
# Sender ID (positions 6-14). Legacy DataApi grammars only accept PB/SO/AA/WR in
# Sender Type, so the validator rewrites numeric prefixes to PB for decode only.
_HDR_IPNN_SENDER_TYPE = re.compile(r"^(HDR)(\d{2})(\d{9})")
_GRH_V22_VERSION = re.compile(r"^(GRH.{8})02\.20")


def normalize_contents_for_decode(contents: str, version: str) -> str:
    """Return file contents adjusted for known library grammar gaps."""
    lines = contents.splitlines(keepends=True)
    if not lines:
        return contents

    normalized: list[str] = []
    for index, line in enumerate(lines):
        body = line.rstrip("\r\n")
        ending = line[len(body):]
        if index == 0 and body.startswith("HDR"):
            body = _normalize_hdr_ipnn(body)
        elif version == "2.2" and body.startswith("GRH"):
            body = _GRH_V22_VERSION.sub(r"\g<1>02.10", body)
        normalized.append(body + ending)
    return "".join(normalized)


def _normalize_hdr_ipnn(hdr_line: str) -> str:
    match = _HDR_IPNN_SENDER_TYPE.match(hdr_line)
    if not match:
        return hdr_line
    prefix, _ipnn_leading, ipnn_tail = match.groups()
    return f"{prefix}PB{ipnn_tail}{hdr_line[14:]}"
