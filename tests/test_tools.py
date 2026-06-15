from tools import search_listings, compare_price


def test_search_returns_results():
    results = search_listings("vintage graphic tee", size=None, max_price=50)
    assert isinstance(results, list)
    assert len(results) > 0


def test_search_no_results():
    results = search_listings("designer ballgown", size="XXS", max_price=5)
    assert results == []


def test_search_price_filter():
    results = search_listings("jacket", size=None, max_price=30)
    assert all(item["price"] <= 30 for item in results)


def test_search_size_filter():
    results = search_listings("tee", size="M", max_price=50)
    assert all("m" in item["size"].lower() for item in results)


def test_compare_price_returns_string():
    results = search_listings("vintage graphic tee", size=None, max_price=50)
    result = compare_price(results[0], results)
    assert isinstance(result, str)
    assert len(result) > 0


def test_compare_price_skips_when_too_few():
    results = search_listings("vintage graphic tee", size=None, max_price=50)
    result = compare_price(results[0], [results[0]])
    assert result == ""