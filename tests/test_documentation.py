import json
import inspect
from pathlib import Path

import substitution_cipher
from substitution_cipher import (
    get_bigrams,
    plausibility,
    prolom_substitute,
    substitute_decrypt,
    substitute_encrypt,
    transition_matrix,
)


FORBIDDEN = [
    "Kra" + "katit",
    "kra" + "katit",
    "TM_ref_" + "combined",
    "TM_ref_" + "kra" + "katit",
    "combined" + "_clean_text",
    "data/" + "processed",
    "data\\" + "processed",
]


def _text(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def test_documentation_does_not_contain_old_references():
    for path in ("README.md", "reports/report.md", "notebooks/demo.ipynb"):
        text = _text(path)
        for forbidden in FORBIDDEN:
            assert forbidden not in text


def test_notebook_is_valid_json_and_cells_have_ids():
    notebook = json.loads(_text("notebooks/demo.ipynb"))
    assert notebook["cells"]
    assert all(cell.get("id") for cell in notebook["cells"])


def test_public_functions_have_docstrings():
    for function in (
        substitute_encrypt,
        substitute_decrypt,
        get_bigrams,
        transition_matrix,
        plausibility,
        prolom_substitute,
        substitution_cipher.SubstitutionCipher,
    ):
        assert inspect.getdoc(function)
