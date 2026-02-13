import os
from grafana_test_utils import save_session, load_session
from datetime import datetime


def test_save_and_load_session(tmp_path):
    p = tmp_path / "sess.json"
    session = {"name": "t1", "created": datetime(2026, 2, 1, 12, 0, 0)}
    save_session(session, str(p))
    loaded = load_session(str(p))
    assert loaded["name"] == "t1"
    assert isinstance(loaded["created"], datetime)
