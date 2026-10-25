import requests
import pytest   

from europapark_crowd import fetch

# if the file already exists the function reads it and skips the download
def test_cached_page_is_not_refetched(tmp_path, monkeypatch):
    (tmp_path / "2023-07.html").write_text("<html>cached</html>", encoding="utf-8")

    def fail(*args, **kwargs):
        raise AssertionError("the network was called")

    # Patch the attribute on the requests module, which fetch.py looks up at call time.
    monkeypatch.setattr(requests, "get", fail)

    assert fetch.fetch_month(2023, 7, raw_dir=tmp_path) == "<html>cached</html>"


def test_2026_is_refused(tmp_path):
    with pytest.raises(ValueError):
        fetch.fetch_month(2026, 7, raw_dir=tmp_path)
