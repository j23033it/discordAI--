from ai_updates.collectors.html_collector import _slugify


def test_slugify_keeps_s_characters_and_normalizes_spaces():
    # 空白をハイフン1つへ正規化できることを確認。
    assert _slugify("Bug fixes") == "bug-fixes"


def test_slugify_collapses_mixed_separators():
    # アンダースコアや複数区切りが混在しても綺麗な slug になることを確認。
    assert _slugify("New_features  -  Codex") == "new-features-codex"
