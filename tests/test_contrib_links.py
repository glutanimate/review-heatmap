from pathlib import Path


def test_contrib_dialog_uses_valid_by_author_link():
    src = (
        Path(__file__).resolve().parents[1]
        / "src"
        / "review_heatmap"
        / "libaddon"
        / "gui"
        / "dialog_contrib.py"
    ).read_text(encoding="utf-8")
    assert "https://ankiweb.net/shared/by-author/225180905" in src
    assert "byauthor/1771074083" not in src
