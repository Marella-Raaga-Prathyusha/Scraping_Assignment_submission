from processing.cleaning import GBP_TO_INR_RATE, clean_price, clean_rating, clean_tags, clean_text, normalize_url, strip_quotes


def test_clean_text():
    assert clean_text("  Hello \n  World \xa0") == "Hello World"


def test_strip_quotes():
    assert strip_quotes('“A quote here”') == "A quote here"


def test_clean_price():
    assert clean_price("£51.77") == round(51.77 * GBP_TO_INR_RATE, 2)


def test_clean_rating():
    assert clean_rating("star-rating Three") == 3


def test_clean_tags():
    assert clean_tags(["Life", "inspirational", "Life"]) == "inspirational;life"


def test_normalize_url():
    assert normalize_url("https://example.com/item") == "https://example.com/item"
    assert normalize_url("/item", "https://example.com/") == "https://example.com/item"
