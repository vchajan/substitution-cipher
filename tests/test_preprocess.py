from subcipher.preprocess import normalize_text


def test_normalize_text_removes_diacritics_and_unsupported_chars():
    assert normalize_text("Příliš žluťoučký kůň!") == "PRILIS_ZLUTOUCKY_KUN"
