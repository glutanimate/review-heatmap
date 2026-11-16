import importlib.util
import sqlite3
import sys
import types
from pathlib import Path
from types import SimpleNamespace


class _FakeDB:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def list(self, sql: str, *args):
        return [row[0] for row in self.conn.execute(sql, args).fetchall()]


def test_rid_search_returns_note_ids_in_notes_mode(monkeypatch):
    conn = sqlite3.connect(":memory:")
    conn.executescript(
        """
        CREATE TABLE cards (id INTEGER PRIMARY KEY, nid INTEGER);
        CREATE TABLE revlog (id INTEGER PRIMARY KEY, cid INTEGER);
        INSERT INTO cards VALUES (101, 10), (102, 10), (103, 20);
        INSERT INTO revlog VALUES (1000, 101), (1500, 102), (2000, 103);
        """
    )

    aqt_mod = types.ModuleType("aqt")
    aqt_mod.mw = SimpleNamespace(col=SimpleNamespace(db=_FakeDB(conn)))
    monkeypatch.setitem(sys.modules, "aqt", aqt_mod)

    finder_path = (
        Path(__file__).resolve().parents[1] / "src" / "review_heatmap" / "finder.py"
    )
    spec = importlib.util.spec_from_file_location("rh_finder", finder_path)
    assert spec is not None and spec.loader is not None
    finder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(finder)

    notes_ctx = SimpleNamespace(
        search="rid:1000:2500",
        ids=[],
        browser=SimpleNamespace(table=SimpleNamespace(is_notes_mode=lambda: True)),
    )
    finder.on_browser_will_search(notes_ctx)
    assert sorted(notes_ctx.ids) == [10, 20]

    cards_ctx = SimpleNamespace(
        search="rid:1000:2500",
        ids=[],
        browser=SimpleNamespace(table=SimpleNamespace(is_notes_mode=lambda: False)),
    )
    finder.on_browser_will_search(cards_ctx)
    assert sorted(cards_ctx.ids) == [101, 102, 103]
