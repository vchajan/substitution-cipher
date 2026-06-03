from substitution_cipher import ALPHABET
from substitution_cipher.preprocess import clean_text


def test_clean_text_removes_diacritics_numbers_and_punctuation():
    raw = "P\u0159\u00edli\u0161 \u017elu\u0165ou\u010dk\u00fd k\u016f\u0148! 123"
    cleaned = clean_text(raw)

    assert cleaned == "PRILIS_ZLUTOUCKY_KUN"
    assert set(cleaned) <= set(ALPHABET)
