from datetime import datetime, timezone

from ai_updates.dispatchers.discord import _format_item
from ai_updates.models import Summary, UpdateItem


def test_format_item_includes_datetime_in_title_and_fixed_layout():
    item = UpdateItem(
        source_id="openai_codex_changelog",
        service="openai",
        title="Codex changelog",
        url="https://developers.openai.com/codex/changelog#new-features-11",
        published_at=datetime(2026, 2, 7, 9, 22, tzinfo=timezone.utc),
        body="dummy",
        fingerprint="fp1",
    )
    summary = Summary(
        headline="Codexの新機能",
        bullets=["A", "B", "C", "D"],
        importance="medium",
        topic="release-note",
    )

    text = _format_item(item, summary)

    assert text.startswith("**Codexの新機能（2026-02-07 18:22 JST）**")
    assert "\n• A\n• B\n• C\n" in text
    assert "• D" not in text
    assert text.endswith("原文: https://developers.openai.com/codex/changelog#new-features-11")
