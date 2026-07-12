from marketing.sections.marketing_sections import get_marketing_nav_items


def test_marketing_nav_items_include_expected_sections():
    sections = get_marketing_nav_items()
    ids = [item["id"] for item in sections]

    assert "landing" in ids
    assert "platform" in ids
    assert "solutions" in ids
    assert "resources" in ids
    assert "pricing" in ids
    assert "about" in ids
    assert "contact" in ids
