# -*- coding: utf-8 -*-

from __future__ import annotations

from types import SimpleNamespace

from cwr_validator.rules import (
    RULE_045_ID,
    RULE_045_MESSAGE,
    check_work_transaction,
    collect_rule_violations,
)


def _work(**kwargs):
    defaults = {
        "record_type": "NWR",
        "title": "HARMONY",
        "submitter_work_n": "R1951",
        "text_music_relationship": "MUS",
        "transaction_sequence_n": 1,
    }
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def _writer(role, record_type="SWR"):
    return SimpleNamespace(record_type=record_type, writer_designation=role)


def test_rule_045_rejects_mus_with_ca():
    violations = check_work_transaction(
        [_work(), _writer("CA")]
    )
    assert len(violations) == 1
    assert violations[0]["rule"] == RULE_045_ID
    assert violations[0]["message"] == RULE_045_MESSAGE
    assert violations[0]["writer_designation"] == "CA"
    assert violations[0]["submitter_work_n"] == "R1951"


def test_rule_045_rejects_each_forbidden_role():
    for role in ("CA", "A", "SA", "TR"):
        violations = check_work_transaction([_work(), _writer(role, "OWR")])
        assert [v["writer_designation"] for v in violations] == [role]


def test_rule_045_allows_mus_with_c_or_ar():
    assert check_work_transaction([_work(), _writer("C")]) == []
    assert check_work_transaction([_work(), _writer("AR")]) == []
    assert check_work_transaction([_work(), _writer("C"), _writer("AR")]) == []


def test_rule_045_ignores_mtx_with_ca():
    assert check_work_transaction(
        [_work(text_music_relationship="MTX"), _writer("CA")]
    ) == []


def test_collect_rule_violations_walks_groups():
    transmission = SimpleNamespace(
        groups=[
            SimpleNamespace(
                transactions=[
                    [_work(title="OK"), _writer("C")],
                    [_work(title="BAD"), _writer("CA")],
                ]
            )
        ]
    )
    violations = collect_rule_violations(transmission)
    assert len(violations) == 1
    assert violations[0]["title"] == "BAD"
