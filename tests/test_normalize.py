from datetime import datetime, timezone

from ai_updates.models import RawItem
from ai_updates.normalize import normalize


def test_normalize_generates_stable_fingerprint():
    # 同じ入力からは毎回同じ fingerprint が生成されることを保証する。
    raw = RawItem(
        source_id="s1",
        service="openai",
        title="  New  Model  ",
        url="https://example.com",
        published_at=datetime.now(timezone.utc),
        body="line1\nline2",
    )
    n1 = normalize(raw)
    n2 = normalize(raw)
    assert n1.fingerprint == n2.fingerprint
    # 余分な空白が除去されることも合わせて確認。
    assert n1.title == "New Model"
