from email.message import EmailMessage

import pytest

from email_import import parse_eml


def test_parse_eml_extracts_subject_body_sender_and_authentication_headers():
    message = EmailMessage()
    message["Subject"] = "GDG Recruitment 2026-2027"
    message["From"] = '"Society Team" <society@example.edu>'
    message["Authentication-Results"] = "mx.example.edu; spf=pass; dkim=pass"
    message["ARC-Authentication-Results"] = "i=1; dmarc=pass"
    message.set_content("Hello students,\n\nApply by Friday.")
    message.add_alternative(
        '<html><body>HTML version <a href="https://example.test/hidden">click here</a>'
        "</body></html>",
        subtype="html",
    )
    message.add_attachment("not part of the message", filename="notes.txt")

    imported = parse_eml(message.as_bytes())

    assert imported.subject == "GDG Recruitment 2026-2027"
    assert imported.sender == "Society Team <society@example.edu>"
    assert imported.body == "Hello students,\n\nApply by Friday."
    assert imported.authentication_results == (
        "mx.example.edu; spf=pass; dkim=pass",
        "i=1; dmarc=pass",
    )
    assert "HTML version" not in imported.body
    assert "not part of the message" not in imported.body
    assert imported.links == ("https://example.test/hidden",)


def test_parse_eml_falls_back_to_readable_text_from_html_only_message():
    raw_email = (
        b"Subject: HTML notice\r\n"
        b"Content-Type: text/html; charset=utf-8\r\n"
        b"\r\n"
        b'<html><body><p>Please review the <b>schedule</b>.</p>'
        b'<a href="https://notice.example.test/urgent">open your notice</a>'
        b"<script>ignored content</script></body></html>"
    )

    imported = parse_eml(raw_email)

    assert imported.subject == "HTML notice"
    assert imported.body == "Please review the schedule. open your notice"
    assert imported.links == ("https://notice.example.test/urgent",)


@pytest.mark.parametrize(
    ("raw_email", "error"),
    [
        (b"", "file is empty"),
        (b"Subject: Empty message\r\n\r\n", "No readable email body"),
    ],
)
def test_parse_eml_rejects_empty_or_bodyless_messages(raw_email, error):
    with pytest.raises(ValueError, match=error):
        parse_eml(raw_email)
