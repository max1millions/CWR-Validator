CWR Validator CLI
=================

Command-line validator for CISAC Common Works Registration (CWR) **v2.1** (``.V21``)
and **v2.2** (``.V22``) files. Parsing uses local checkouts of the CWR DataApi
library — the same forks used by CWR-INTERFACE generators — not the legacy PyPI
``CWR-API`` package.

Validation means the file decodes successfully through ``default_file_decoder()``
from the selected library version. This confirms structural parseability against
that library's grammar; it is not a full CISAC business-rule audit.

HDR IPNN workaround (11-digit sender IDs)
-------------------------------------------

CWR 2.1 Rev 8 and 2.2 Rev 2 allow publishers whose IPI Name Number exceeds nine
digits to place the leading two digits in the HDR **Sender Type** field and the
remaining nine in **Sender ID** (see ``CWR-INTERFACE/VERSIONS.md``). The
validator rewrites that HDR layout to ``PB`` + nine-digit tail before calling the
DataApi decoder, because the upstream library grammars only accept ``PB`` /
``SO`` / ``AA`` / ``WR`` in Sender Type. For v2.2 files it also maps GRH
``02.20`` to ``02.10`` for the same decode pass. These are decode-time shims
inside ``cwr_validator/preprocess.py``; the on-disk file is never modified.

Requirements
------------

- Python 3.11+
- Local CWR DataApi checkouts for v2.1 and v2.2 (see **Library paths** below)
- ``pyparsing`` and ``pyyaml`` (installed via ``requirements.txt``)

Quick start
-----------

From the CWR-INTERFACE repo (default sibling layout under ``LIBRARIES/``)::

    cd LIBRARIES/CWR-Validator
    pip install -r requirements.txt
    python validate_cwr.py ../../OUTPUT/CW260001RIT_088.V22
    python validate_cwr.py --version 2.1 path/to/file.V21

Or after ``pip install -e .``::

    validate-cwr path/to/file.V22

CLI options
-----------

``--version {2.1,2.2}``
    Force CWR version for all files. Must match ``.V21`` / ``.V22`` extension when present.

``--json``
    Emit machine-readable JSON per file.

``-q`` / ``--quiet``
    Only print failures.

``-v`` / ``--verbose``
    Include group and transaction counts on success.

**Exit codes:** ``0`` all passed, ``1`` any failure, ``2`` configuration error.

Library paths
-------------

Each version uses a separate checkout because both libraries expose the ``cwr``
package name. The CLI runs one **subprocess per file** so imports do not collide.

Configure paths in one of these ways (highest precedence first):

+---------------------------+------------------------------------------+
| Source                    | Key / variable                           |
+===========================+==========================================+
| Environment               | ``CWR_LIBRARY_V21_PATH``,                |
|                           | ``CWR_LIBRARY_V22_PATH``                 |
+---------------------------+------------------------------------------+
| ``data_validator/         | ``library.v21.path``,                    |
| config.properties``       | ``library.v22.path``                     |
+---------------------------+------------------------------------------+
| Default                   | ``../CWR_LIBRARY_V2.1``,                 |
|                           | ``../CWR_LIBRARY_V2.2``                  |
+---------------------------+------------------------------------------+

Paths may be absolute or relative to the CWR-Validator submodule root. See
``.env.example`` for a template.

Development
-----------

::

    pip install -r requirements.txt
    pytest

Optional integration tests (``pytest -m integration``) decode a built-in v2.1
fixture through the real library stack; they are skipped when the environment's
pyparsing / library combination cannot parse.

License
-------

MIT — see ``LICENSE``.
