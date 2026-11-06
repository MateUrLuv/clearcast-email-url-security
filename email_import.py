"""Local parsing helpers for original RFC 5322 email files."""
from dataclasses import dataclass
from email import policy
from email.message import Message
from email.parser import BytesParser
from html.parser import HTMLParser
import re


@dataclass(frozen=True)
class ImportedEmail:
    subject: str
    body: str
    sender: str
    authentication_results: tuple[str, ...]
    links: tuple[str, ...]


class _HTMLTextExtractor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.links = []
        self._suppressed_tags = 0

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style"}:
            self._suppressed_tags += 1
        if tag == "a":
            href = dict(attrs).get("href", "").strip()
            if re.match(r"https?://", href, re.IGNORECASE):
                self.links.append(href.rstrip(".,;:!?)]}"))

    def handle_endtag(self, tag):
        if tag in {"script", "style"} and self._suppressed_tags:
            self._suppressed_tags -= 1

    def handle_data(self, data):
        if not self._suppressed_tags:
            self.parts.append(data)


def _read_text_part(part: Message) -> str:
    content = part.get_content()
    if isinstance(content, bytes):
        charset = part.get_content_charset() or "utf-8"
        content = content.decode(charset)
    return content.strip()


def _html_to_text(content: str) -> str:
    parser = _HTMLTextExtractor()
    parser.feed(content)
    parser.close()
    text = " ".join(" ".join(parser.parts).split())
    return re.sub(r"\s+([,.;:!?])", r"\1", text)


def _html_links(content: str) -> tuple[str, ...]:
    parser = _HTMLTextExtractor()
    parser.feed(content)
    parser.close()
    return tuple(dict.fromkeys(parser.links))


def parse_eml(raw_email: bytes) -> ImportedEmail:
    """Extract the subject, readable body, and selected original headers."""
    if not raw_email:
        raise ValueError("The selected email file is empty.")

    try:
        message = BytesParser(policy=policy.default).parsebytes(raw_email)
    except (TypeError, ValueError) as error:
        raise ValueError("ClearCast could not read this original email file.") from error

    plain_parts = [
        part for part in message.walk()
        if part.get_content_type() == "text/plain"
        and part.get_content_disposition() != "attachment"
        and not part.get_filename()
    ]
    html_parts = [
        part for part in message.walk()
        if part.get_content_type() == "text/html"
        and part.get_content_disposition() != "attachment"
        and not part.get_filename()
    ]

    body = ""
    links = []
    try:
        if plain_parts:
            body = _read_text_part(plain_parts[0])
        elif html_parts:
            body = _html_to_text(_read_text_part(html_parts[0]))
        for part in html_parts:
            links.extend(_html_links(_read_text_part(part)))
    except (LookupError, UnicodeError) as error:
        raise ValueError(
            "ClearCast could not decode the email body. Export the original message "
            "again or paste its text instead."
        ) from error

    if not body:
        raise ValueError("No readable email body was found in this file.")

    authentication_results = tuple(
        str(value).strip()
        for header in ("Authentication-Results", "ARC-Authentication-Results")
        for value in message.get_all(header, [])
        if str(value).strip()
    )
    return ImportedEmail(
        subject=str(message.get("Subject", "")).strip(),
        body=body,
        sender=str(message.get("From", "")).strip(),
        authentication_results=authentication_results,
        links=tuple(dict.fromkeys(links)),
    )
