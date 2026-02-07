from ai_updates.collectors.html_collector import _slugify


def test_slugify_keeps_s_characters_and_normalizes_spaces():
    assert _slugify("Bug fixes") == "bug-fixes"


def test_slugify_collapses_mixed_separators():
    assert _slugify("New_features  -  Codex") == "new-features-codex"
