from ml.email_urls import extract_urls


def test_extract_urls_deduplicates_and_trims_punctuation():
    text = 'See (https://example.com/login), then https://example.com/login. Also https://other.test/x?y=1!'
    assert extract_urls(text) == ['https://example.com/login', 'https://other.test/x?y=1']


def test_extract_urls_has_a_limit():
    text = ' '.join(f'https://example.com/{i}' for i in range(10))
    assert len(extract_urls(text)) == 5


def test_extract_urls_finds_plain_text_domains_without_a_hyperlink():
    text = "Visit www.account-review.example/login or account-review.example/reset?next=1."
    assert extract_urls(text) == [
        "www.account-review.example/login",
        "account-review.example/reset?next=1",
    ]


def test_extract_urls_does_not_extract_email_address_domains():
    assert extract_urls("Contact support@example.com for help.") == []
