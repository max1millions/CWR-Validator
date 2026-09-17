# -*- coding: utf-8 -*-
"""CISAC CWR transaction rules the DataApi grammar does not enforce.

These run after a successful decode. A violation fails validation the same
way a parse error does, so generators cannot increment a CWR sequence on a
file a society would transaction-reject (TR).
"""

from __future__ import annotations

from typing import Any, Iterable

# CWR 2.2 Rev 2 §4.4 work-transaction edit 45 (MusicMark validation number 045).
RULE_045_ID = "045"
RULE_045_MESSAGE = (
    "Text Music Indicator is MUS with a CA, A, SA, or TR SWR/OWR record"
)
MUS_FORBIDDEN_WRITER_ROLES = frozenset({"CA", "A", "SA", "TR"})
WORK_RECORD_TYPES = frozenset({"NWR", "REV", "ISW", "EXC"})
WRITER_RECORD_TYPES = frozenset({"SWR", "OWR"})


def _code(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip().upper()


def collect_rule_violations(transmission: Any) -> list[dict[str, Any]]:
    """Return CISAC TR violations found on a decoded CWR transmission."""
    violations: list[dict[str, Any]] = []
    for group in getattr(transmission, "groups", None) or ():
        for transaction in getattr(group, "transactions", None) or ():
            violations.extend(check_work_transaction(transaction))
    return violations


def check_work_transaction(records: Iterable[Any]) -> list[dict[str, Any]]:
    """Apply work-transaction TRs to one NWR/REV/ISW/EXC record group."""
    work = None
    writers: list[Any] = []
    for rec in records:
        record_type = _code(getattr(rec, "record_type", ""))
        if record_type in WORK_RECORD_TYPES:
            work = rec
        elif record_type in WRITER_RECORD_TYPES:
            writers.append(rec)
    if work is None:
        return []
    return _check_rule_045(work, writers)


def _check_rule_045(work: Any, writers: list[Any]) -> list[dict[str, Any]]:
    """Rule 45: MUS works may only use writer designations C or AR."""
    if _code(getattr(work, "text_music_relationship", None)) != "MUS":
        return []
    title = str(getattr(work, "title", "") or "").strip()
    submitter = str(getattr(work, "submitter_work_n", "") or "").strip()
    txn = getattr(work, "transaction_sequence_n", None)
    violations: list[dict[str, Any]] = []
    for writer in writers:
        role = _code(getattr(writer, "writer_designation", None))
        if role not in MUS_FORBIDDEN_WRITER_ROLES:
            continue
        violations.append(
            {
                "rule": RULE_045_ID,
                "message": RULE_045_MESSAGE,
                "title": title,
                "submitter_work_n": submitter,
                "writer_designation": role,
                "record_type": _code(getattr(writer, "record_type", "")),
                "transaction_sequence_n": txn,
            }
        )
    return violations
