import sqlite3

import pytest

from review_history import ReviewHistory


def test_history_detects_normalized_email_repeat_without_storing_content(tmp_path):
    history_path = tmp_path / "reviews.sqlite3"
    history = ReviewHistory(history_path)

    assert not history.record(
        "Email", "Subject: Meeting\nBody: Hello there", 0.1, 0.5, "Pasted email"
    )
    assert history.record(
        "Email", " subject: meeting   body: hello there ", 0.1, 0.5, "Pasted email"
    )

    recent = history.recent()
    assert len(recent) == 2
    assert recent[0]["prior_reviews"] == 1
    assert recent[1]["prior_reviews"] == 0
    with sqlite3.connect(history_path) as connection:
        stored_values = repr(connection.execute("SELECT * FROM reviews").fetchall())
    assert "Hello there" not in stored_values
    assert "Subject: Meeting" not in stored_values


def test_history_matches_urls_across_review_sources(tmp_path):
    history_path = tmp_path / "reviews.sqlite3"
    history = ReviewHistory(history_path)

    assert not history.record("URL", "www.example.test/a", 0.8, 0.52, "Email")
    reopened_history = ReviewHistory(history_path)
    assert reopened_history.record(
        "URL", "https://www.example.test/a", 0.8, 0.52, "Direct URL"
    )

    recent = reopened_history.recent()
    assert recent[0]["item_type"] == "URL"
    assert recent[0]["source"] == "Direct URL"
    assert recent[0]["prior_reviews"] == 1


def test_history_rejects_unknown_item_type(tmp_path):
    history = ReviewHistory(tmp_path / "reviews.sqlite3")

    with pytest.raises(ValueError, match="Email or URL"):
        history.record("Attachment", "file content", 0.1, 0.5, "Email")


def test_history_can_be_cleared(tmp_path):
    history = ReviewHistory(tmp_path / "reviews.sqlite3")
    history.record("URL", "https://example.test", 0.1, 0.52, "Direct URL")

    history.clear()

    assert history.recent() == []
