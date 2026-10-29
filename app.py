"""ClearCast: an explainable phishing investigation demo."""
import html
import json
from pathlib import Path

import joblib
import pandas as pd
import streamlit as st

from ml.email_urls import extract_urls
from ml.explanations import explain_email, explain_url
from ml.url_model import normalized_url

ROOT = Path(__file__).resolve().parent
REPORT = json.loads((ROOT / "reports" / "held_out.json").read_text())
URL_THRESHOLD = REPORT["url"]["threshold"]
EXTERNAL_PATH = ROOT / "reports" / "external.json"

st.set_page_config(
    page_title="ClearCast | Email security",
    page_icon="✳",
    layout="wide",
    initial_sidebar_state="auto",
)

st.markdown("""
<style>
:root {
  --paper: #f5f3ed;
  --surface: #fffefa;
  --surface-soft: #eeece4;
  --ink: #1d2925;
  --muted: #64716b;
  --line: #dedfd5;
  --forest: #315d4a;
  --forest-soft: #e7eee8;
  --coral: #a9473e;
  --coral-soft: #f6e8e4;
}
.stApp { background: var(--paper); color: var(--ink); }
html, body, [class*="css"] {
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont,
    "Segoe UI", sans-serif;
}
.block-container { max-width: 1180px; padding: 2rem 2.4rem 4rem; }
h1, h2, h3, h4 { color: var(--ink); letter-spacing: -.035em; }
h1 { font-size: clamp(2rem, 3.2vw, 2.8rem) !important; line-height: 1.12 !important; }
h2 { font-size: 1.55rem !important; }
h3 { font-size: 1.2rem !important; }
p, li { color: var(--muted); line-height: 1.65; }
[data-testid="stSidebar"] {
  background: #eeece4; border-right: 1px solid var(--line);
}
[data-testid="stSidebar"] > div:first-child { padding-top: 1.5rem; }
[data-testid="stSidebar"] [data-testid="stRadio"] label { font-weight: 560; }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color: var(--muted); }
[data-testid="stMetric"] {
  background: var(--surface); border: 1px solid var(--line);
  border-radius: 12px; padding: 15px 17px;
}
[data-testid="stMetricLabel"] { color: var(--muted); }
[data-testid="stMetricValue"] { color: var(--ink); }
.stButton button[kind="primary"], [data-testid="stFormSubmitButton"] button {
  background: #294d3d; color: #ffffff !important; border: 1px solid #294d3d;
  border-radius: 8px; font-weight: 700; min-height: 2.7rem;
  transition: background-color .15s ease, box-shadow .15s ease;
}
.stButton button[kind="primary"] *, [data-testid="stFormSubmitButton"] button * {
  color: #ffffff !important; -webkit-text-fill-color: #ffffff !important;
}
.stButton button[kind="primary"]:hover,
[data-testid="stFormSubmitButton"] button:hover {
  background: #1d3d2f; color: #ffffff !important; border-color: #1d3d2f;
  box-shadow: 0 3px 9px rgba(29, 61, 47, .2);
}
.stButton button[kind="primary"]:focus-visible,
[data-testid="stFormSubmitButton"] button:focus-visible {
  outline: 3px solid #a9473e !important; outline-offset: 3px;
  box-shadow: 0 0 0 2px var(--surface);
}
.stButton button:not([kind="primary"]) {
  border-color: #c9cfc5; color: #34443c; border-radius: 8px;
}
[data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea {
  background: var(--surface); border-color: #cfd3ca; border-radius: 8px;
}
[data-testid="stTextInput"] input:focus, [data-testid="stTextArea"] textarea:focus {
  border-color: var(--forest); box-shadow: 0 0 0 1px var(--forest);
}
[data-testid="stDataFrame"] { border: 1px solid var(--line); border-radius: 9px; }
div[data-testid="stVerticalBlockBorderWrapper"] {
  background: var(--surface); border: 1px solid var(--line);
  border-radius: 14px; padding: 1.15rem 1.3rem;
}
.cc-wordmark { font-size: 1.68rem; font-weight: 760; letter-spacing: -.065em; color: var(--ink); }
.cc-wordmark-mark { color: var(--forest); font-size: 1.8rem; }
.cc-sidebar-note {
  border-top: 1px solid #d5d6cd; margin-top: 1.5rem; padding-top: 1rem;
  color: var(--muted); font-size: .82rem; line-height: 1.55;
}
.cc-masthead {
  display: flex; justify-content: space-between; align-items: center;
  gap: 1rem; border-bottom: 1px solid var(--line); padding-bottom: .85rem;
  margin-bottom: 2rem;
}
.cc-masthead-brand { font-size: 1rem; font-weight: 750; letter-spacing: -.03em; }
.cc-masthead-tag {
  color: var(--muted); font-size: .82rem; border: 1px solid var(--line);
  border-radius: 999px; padding: .35rem .7rem;
}
.cc-overline {
  color: var(--forest); font-size: .75rem; font-weight: 700;
  letter-spacing: .09em; text-transform: uppercase; margin-bottom: .55rem;
}
.cc-intro { max-width: 690px; font-size: 1rem; margin: .55rem 0 1.45rem; }
.cc-workspace-heading {
  color: var(--ink); font-size: .95rem; font-weight: 680;
  margin: .2rem 0 .1rem;
}
.cc-workspace-help { color: var(--muted); font-size: .82rem; margin: 0 0 .85rem; }
.cc-gmail-note {
  color: #6b716b; font-size: .79rem; border-top: 1px solid var(--line);
  margin-top: 1.15rem; padding-top: .8rem;
}
.cc-result-rule { border-top: 1px solid var(--line); margin: 1.8rem 0 1.2rem; }
.cc-result-panel {
  display: grid; grid-template-columns: minmax(165px, .75fr) minmax(0, 1.7fr);
  gap: .75rem 1.5rem; align-items: center;
  background: var(--surface); border: 1px solid var(--line);
  border-radius: 14px; padding: 1.25rem 1.4rem; margin: .55rem 0 1.1rem;
}
.cc-result-score-label { color: var(--muted); font-size: .8rem; margin-bottom: .12rem; }
.cc-result-score { color: var(--ink); font-size: 2.65rem; font-weight: 750; letter-spacing: -.06em; line-height: 1.15; }
.cc-result-score-note { color: var(--muted); font-size: .75rem; margin-top: .2rem; line-height: 1.45; }
.cc-assessment {
  border-left: 4px solid var(--forest); padding: .3rem 0 .3rem 1rem;
}
.cc-assessment.alert { border-left-color: var(--coral); }
.cc-assessment-label { color: var(--muted); font-size: .78rem; margin-bottom: .25rem; }
.cc-assessment-title { color: var(--ink); font-weight: 740; font-size: 1.25rem; line-height: 1.3; }
.cc-assessment-copy { color: var(--muted); font-size: .88rem; margin-top: .24rem; line-height: 1.5; }
.cc-threshold-note { color: var(--muted); font-size: .81rem; margin-top: .45rem; }
.cc-next-step { color: var(--ink); font-size: .82rem; margin-top: .38rem; line-height: 1.5; }
.cc-gauge { grid-column: 1 / -1; margin: .4rem 0 0; }
.cc-gauge-track { height: 8px; background: #e4e5dd; border-radius: 20px; position: relative; }
.cc-gauge-fill { height: 8px; border-radius: 20px; }
.cc-gauge-cutoff { position: absolute; top: -4px; width: 2px; height: 16px; background: #37463e; }
.cc-gauge-labels {
  display: flex; justify-content: space-between; gap: .5rem;
  color: var(--muted); font-size: .73rem; margin-top: .4rem;
}
.cc-legend {
  display: flex; flex-wrap: wrap; gap: .65rem 1.3rem; margin: .5rem 0 .7rem;
  color: var(--muted); font-size: .79rem;
}
.cc-legend-up { color: #963c34; font-weight: 650; }
.cc-legend-down { color: #315d4a; font-weight: 650; }
.cc-feature {
  background: var(--surface); border: 1px solid var(--line);
  border-radius: 9px; padding: .62rem .75rem; margin: .36rem 0;
}
.cc-feature-head { display: flex; justify-content: space-between; align-items: baseline; gap: .7rem; }
.cc-feature-name { color: var(--ink); font-size: .84rem; overflow-wrap: anywhere; }
.cc-feature-value { font-size: .76rem; font-weight: 700; white-space: nowrap; }
.cc-feature-track { height: 4px; background: #e7e8e1; border-radius: 8px; margin-top: .45rem; }
.cc-feature-fill { height: 4px; border-radius: 8px; }
.cc-positive { color: #963c34; }
.cc-negative { color: #315d4a; }
.cc-section-break {
  border-top: 1px solid var(--line); padding-top: 1.5rem; margin-top: 1.5rem;
}
.cc-small-note {
  color: var(--muted); background: var(--surface-soft); border-radius: 9px;
  padding: .8rem 1rem; font-size: .85rem; line-height: 1.6;
}
@media (max-width: 760px) {
  .block-container { padding: 1.2rem 1rem 3rem; }
  .cc-masthead { margin-bottom: 1.4rem; }
  .cc-masthead-tag { text-align: right; }
  .cc-result-panel { grid-template-columns: 1fr; gap: .75rem; padding: 1rem; }
  .cc-gauge { grid-column: 1; }
  .cc-feature-head { align-items: flex-start; }
}
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_model(name):
    return joblib.load(ROOT / "artifacts" / f"{name}_model.joblib")


def verdict(score, threshold):
    if score >= threshold:
        return "Review as phishing", "The model found phishing-like patterns. Check the context before acting."
    return "No phishing signal detected", "The model found fewer phishing-like patterns. This is not a safety guarantee."


def show_score(score, threshold, model_name):
    label, detail = verdict(score, threshold)
    positive = score >= threshold
    next_step = (
        "Don't use the link or share information until the sender is verified through a trusted channel."
        if positive else
        "This result is not a safety guarantee; verify anything unexpected independently before acting."
    )
    st.markdown(
        f'<section class="cc-result-panel" aria-label="{html.escape(model_name)} analysis result">'
        f'<div><div class="cc-result-score-label">{html.escape(model_name)} model score</div>'
        f'<div class="cc-result-score">{score:.1%}</div>'
        f'<div class="cc-result-score-note">Model output, not a calibrated real-world probability.</div></div>'
        f'<div><div class="cc-assessment {"alert" if positive else ""}">'
        f'<div class="cc-assessment-label">Assessment</div>'
        f'<div class="cc-assessment-title">{html.escape(label)}</div>'
        f'<div class="cc-assessment-copy">{html.escape(detail)}</div></div>'
        f'<div class="cc-threshold-note">Decision threshold: <strong>{threshold:.0%}</strong></div>'
        f'<div class="cc-next-step"><strong>Suggested next step:</strong> {html.escape(next_step)}</div></div>'
        f'<div class="cc-gauge"><div class="cc-gauge-track">'
        f'<div class="cc-gauge-fill" style="width:{min(max(score, 0), 1) * 100:.2f}%;'
        f'background:{"#a9473e" if positive else "#477b60"}"></div>'
        f'<span class="cc-gauge-cutoff" style="left:{threshold * 100:.2f}%"></span>'
        f'</div><div class="cc-gauge-labels"><span>0</span>'
        f'<span>Model output scale &nbsp;·&nbsp; vertical marker = decision threshold</span>'
        f'<span>100</span></div></div></section>',
        unsafe_allow_html=True,
    )


def show_contributions(items, limit=None):
    """Render signed linear contributions as accessible, compact bars."""
    items = items[:limit] if limit is not None else items
    st.markdown(
        '<div class="cc-legend"><span class="cc-legend-up">↑ Raises phishing score</span>'
        '<span class="cc-legend-down">↓ Lowers phishing score; not proof of safety</span></div>',
        unsafe_allow_html=True,
    )
    if not items:
        st.caption("No learned features were available for this input.")
        return
    max_magnitude = max((abs(item["contribution"]) for item in items), default=0) or 1
    for item in items:
        contribution = float(item["contribution"])
        positive = contribution > 0
        color = "#a9473e" if positive else "#477b60"
        direction = "↑ Raises phishing score" if positive else "↓ Lowers phishing score"
        magnitude = abs(contribution) / max_magnitude * 100
        name = html.escape(str(item["feature"]))
        value = f"{contribution:+.3f}"
        st.markdown(
            f'<div class="cc-feature"><div class="cc-feature-head">'
            f'<span class="cc-feature-name">{name}</span>'
            f'<span class="cc-feature-value {"cc-positive" if positive else "cc-negative"}">'
            f'{direction} &nbsp; {value}</span></div>'
            f'<div class="cc-feature-track"><div class="cc-feature-fill" '
            f'style="width:{magnitude:.1f}%;background:{color}"></div></div></div>',
            unsafe_allow_html=True,
        )


def show_url_features(model, url, limit=6):
    text_col, structure_col = st.columns(2)
    with text_col:
        st.markdown("#### URL text patterns")
        st.caption("Character patterns from the trained text component.")
        show_contributions(explain_url(model, url, limit, "text"))
    with structure_col:
        st.markdown("#### URL structure")
        st.caption("Numeric features from the same trained classifier.")
        show_contributions(explain_url(model, url, limit, "structure"))


def show_confusion_matrix(result):
    cm = result["confusion_matrix"]
    frame = pd.DataFrame(
        [[cm["true_negative"], cm["false_positive"]],
         [cm["false_negative"], cm["true_positive"]]],
        index=["Actually legitimate", "Actually phishing"],
        columns=["Predicted legitimate", "Predicted phishing"],
    )
    st.dataframe(frame, use_container_width=True)


def show_benchmark(result):
    metrics = [
        ("Examples", f"{result['held_out_count']:,}"),
        ("Precision", f"{result['precision']:.1%}"),
        ("Recall", f"{result['recall']:.1%}"),
        ("F1", f"{result['f1']:.1%}"),
        ("False-positive rate", f"{result['false_positive_rate']:.1%}"),
        ("Decision threshold", f"{result['threshold']:.0%}"),
    ]
    metric_columns = st.columns(3)
    for index, (label, value) in enumerate(metrics):
        metric_columns[index % len(metric_columns)].metric(label, value)
    st.markdown("**Confusion matrix**")
    show_confusion_matrix(result)


def show_embedded_urls(links):
    if not links:
        st.caption("No HTTP or HTTPS URLs found in this message.")
        return
    st.markdown(f"#### Links found in this message · {len(links)}")
    st.caption("Each link is assessed independently; URL scores do not change the email verdict.")
    url_model = None
    for item in links:
        link = item["url"]
        score = item["score"]
        with st.expander(f"{'Review' if score >= URL_THRESHOLD else 'Below threshold'} · {score:.1%} · {link[:90]}"):
            st.code(link, language=None)
            show_score(score, URL_THRESHOLD, "URL")
            st.markdown("**What influenced this URL score**")
            if url_model is None:
                url_model = load_model("url")
            show_contributions(explain_url(url_model, link, 4))


def analyze_email_callback():
    subject = st.session_state.get("email_subject", "")
    body = st.session_state.get("email_body", "")
    content = f"{subject}\n{body}".strip()
    if not content:
        st.session_state.pop("email_analysis", None)
        st.session_state["email_analysis_error"] = "Add a subject or message before analyzing."
        return

    model = load_model("email")
    score = float(model.predict_proba([content])[0, 1])
    links = []
    url_model = None
    for link in extract_urls(content):
        try:
            normalized_url(link)
        except ValueError:
            continue
        if url_model is None:
            url_model = load_model("url")
        links.append({
            "url": link,
            "score": float(url_model.predict_proba([link])[0, 1]),
        })
    st.session_state.email_analysis = {
        "score": score,
        "features": explain_email(model, content, 10),
        "links": links,
    }
    st.session_state.pop("email_analysis_error", None)


def analyze_url_callback():
    url = st.session_state.get("url_input", "")
    try:
        normalized_url(url)
    except ValueError as error:
        st.session_state.pop("url_analysis", None)
        st.session_state["url_analysis_error"] = str(error)
        return

    model = load_model("url")
    st.session_state.url_analysis = {
        "url": url,
        "score": float(model.predict_proba([url])[0, 1]),
    }
    st.session_state.pop("url_analysis_error", None)


@st.cache_data
def load_external_report():
    if not EXTERNAL_PATH.exists():
        return None
    return json.loads(EXTERNAL_PATH.read_text())


with st.sidebar:
    st.markdown(
        '<div class="cc-wordmark"><span class="cc-wordmark-mark">✳</span> ClearCast</div>',
        unsafe_allow_html=True,
    )
    st.write("")
    st.markdown("**Workspace**")
    section = st.radio(
        "Choose a workspace",
        ["Email investigation", "URL investigation", "Evidence & evaluation"],
        index=0,
        label_visibility="collapsed",
        key="navigation_section",
    )
    st.markdown(
        '<div class="cc-sidebar-note"><strong>Private by design</strong><br>'
        'Analysis runs locally. ClearCast never visits a URL or retrieves page content.</div>',
        unsafe_allow_html=True,
    )

st.markdown(
    '<div class="cc-masthead"><span class="cc-masthead-brand">CLEARCAST &nbsp; / &nbsp; '
    'INVESTIGATIONS</span><span class="cc-masthead-tag">Local analysis</span></div>',
    unsafe_allow_html=True,
)

if section == "Email investigation":
    st.markdown('<div class="cc-overline">Message review</div>', unsafe_allow_html=True)
    st.title("A second look at a suspicious email.")
    st.markdown(
        '<div class="cc-intro">Paste a message to see what the email model notices. '
        'Any links in it are scored separately, so a link result never changes the email assessment.</div>',
        unsafe_allow_html=True,
    )

    email_analysis = st.session_state.get("email_analysis")
    if email_analysis:
        st.markdown('<div class="cc-result-rule"></div>', unsafe_allow_html=True)
        st.markdown('<div class="cc-overline">Email assessment</div>', unsafe_allow_html=True)
        show_score(email_analysis["score"], REPORT["email"]["threshold"], "Email")
        st.markdown("#### What influenced the email score")
        show_contributions(email_analysis["features"])
        st.markdown('<div class="cc-section-break"></div>', unsafe_allow_html=True)
        show_embedded_urls(email_analysis["links"])
    elif st.session_state.get("email_analysis_error"):
        st.warning(st.session_state["email_analysis_error"])
    else:
        st.caption("Your analysis will appear here, with the score, threshold, and signals explained.")

    suspicious_sample_col, legitimate_sample_col, _ = st.columns([1.8, 1.8, 4.4])
    if suspicious_sample_col.button("Load suspicious sample", use_container_width=True):
        st.session_state["email_subject"] = "Urgent: verify your account"
        st.session_state["email_body"] = (
            "Dear customer, verify your account immediately or access may be restricted. "
            "Review your account here: https://secure-account-check.example/login"
        )
        st.session_state.pop("email_analysis", None)
        st.session_state.pop("email_analysis_error", None)
    if legitimate_sample_col.button("Load legitimate sample", use_container_width=True):
        st.session_state["email_subject"] = "Project notes for Thursday"
        st.session_state["email_body"] = (
            "Hi team, I have attached the notes from our planning session. "
            "Please add any updates before Thursday's meeting."
        )
        st.session_state.pop("email_analysis", None)
        st.session_state.pop("email_analysis_error", None)

    form_col, context_col = st.columns([1.8, 1])
    with form_col:
        with st.container(border=True):
            st.markdown('<div class="cc-workspace-heading">Paste email</div>', unsafe_allow_html=True)
            st.markdown(
                '<div class="cc-workspace-help">Enter the subject and message body below. '
                'No inbox access or upload is needed.</div>',
                unsafe_allow_html=True,
            )
            with st.form("email_investigation", border=False):
                subject = st.text_input("Subject", key="email_subject", placeholder="Subject line")
                body = st.text_area(
                    "Message", key="email_body", height=205,
                    placeholder="Paste the email message here",
                    help="The email model analyzes the subject and message text together.",
                )
                st.form_submit_button(
                    "Analyze email", type="primary", use_container_width=True,
                    on_click=analyze_email_callback,
                )
            st.markdown(
                '<div class="cc-gmail-note">Import from Gmail is coming later. '
                'This demo uses pasted email text only.</div>',
                unsafe_allow_html=True,
            )
    with context_col:
        st.markdown("#### What happens next")
        st.markdown(
            "The email model reviews the subject and body. Its learned word and phrase signals "
            "are shown with the result."
        )
        st.markdown(
            "Links are detected from the pasted text and assessed by a separate URL model. "
            "The app does not open them."
        )
        st.markdown(
            '<div class="cc-small-note"><strong>How to read the score</strong><br>'
            'It is a model output compared with a displayed decision threshold—not a '
            'calibrated real-world probability or a guarantee of safety.</div>',
            unsafe_allow_html=True,
        )

elif section == "URL investigation":
    st.markdown('<div class="cc-overline">Link review</div>', unsafe_allow_html=True)
    st.title("Look at the link, not the website.")
    st.markdown(
        '<div class="cc-intro">ClearCast analyzes the URL text only. It never visits the website, '
        'downloads its page, or follows redirects.</div>',
        unsafe_allow_html=True,
    )

    url_analysis = st.session_state.get("url_analysis")
    if url_analysis:
        st.markdown('<div class="cc-result-rule"></div>', unsafe_allow_html=True)
        st.markdown(f"**Address reviewed:** `{url_analysis['url']}`")
        show_score(url_analysis["score"], URL_THRESHOLD, "URL")
        st.markdown("#### What influenced the URL score")
        show_url_features(load_model("url"), url_analysis["url"])
    elif st.session_state.get("url_analysis_error"):
        st.warning(st.session_state["url_analysis_error"])
    else:
        st.caption("Your URL assessment and feature contributions will appear here.")

    suspicious_sample_col, legitimate_sample_col, _ = st.columns([1.8, 1.8, 4.4])
    if suspicious_sample_col.button(
        "Load suspicious sample", use_container_width=True, key="url_suspicious_sample",
    ):
        st.session_state["url_input"] = "https://secure-account-check.example/login"
        st.session_state.pop("url_analysis", None)
        st.session_state.pop("url_analysis_error", None)
    if legitimate_sample_col.button(
        "Load legitimate sample", use_container_width=True, key="url_legitimate_sample",
    ):
        st.session_state["url_input"] = "https://www.example.org/about"
        st.session_state.pop("url_analysis", None)
        st.session_state.pop("url_analysis_error", None)

    form_col, context_col = st.columns([1.8, 1])
    with form_col:
        with st.container(border=True):
            st.markdown('<div class="cc-workspace-heading">Paste a URL</div>', unsafe_allow_html=True)
            st.markdown(
                '<div class="cc-workspace-help">Use the complete address if available. '
                'No network request is made.</div>',
                unsafe_allow_html=True,
            )
            with st.form("url_investigation", border=False):
                url = st.text_input(
                    "URL", key="url_input", placeholder="https://example.com/account",
                    help="HTTP and HTTPS URLs are accepted. Bare hostnames are also supported.",
                )
                st.form_submit_button(
                    "Analyze URL", type="primary", use_container_width=True,
                    on_click=analyze_url_callback,
                )
    with context_col:
        st.markdown("#### What we inspect")
        st.markdown(
            "The URL model considers learned character patterns and structural details "
            "from the address itself."
        )
        st.markdown(
            '<div class="cc-small-note"><strong>Privacy boundary</strong><br>'
            'The destination is never contacted. A result cannot confirm what a live '
            'webpage contains.</div>',
            unsafe_allow_html=True,
        )

else:
    st.markdown('<div class="cc-overline">Model evidence</div>', unsafe_allow_html=True)
    st.title("What the evaluation can—and cannot—tell us.")
    st.markdown(
        '<div class="cc-intro">Held-out and external-source results are kept separate. '
        'These are research benchmarks on curated datasets, not expected live-traffic performance.</div>',
        unsafe_allow_html=True,
    )

    st.markdown("### Held-out test")
    st.caption(
        "Email data is deduplicated and split 80/20 with stratification. URL data is deduplicated, "
        "sampled evenly by class, and split by hostname into training, validation, and held-out test."
    )
    st.caption(
        f"Email threshold: {REPORT['email']['threshold']:.0%}. URL threshold: "
        f"{REPORT['url']['threshold']:.0%}, chosen on validation data for a 3% false-positive target."
    )
    for task in ("email", "url"):
        with st.container(border=True):
            st.markdown(f"#### {task.title()} model")
            show_benchmark(REPORT[task])

    external = load_external_report()
    if external:
        st.markdown('<div class="cc-section-break"></div>', unsafe_allow_html=True)
        st.markdown("### External-source stress test")
        st.caption(
            "The trained models are evaluated without fitting or threshold tuning on these examples. "
            "Known overlap is removed: email text hashes and URL hostnames from the source corpus."
        )
        for task in ("email", "url"):
            result = external[task]
            with st.container(border=True):
                st.markdown(f"#### {task.title()} · external source")
                st.caption(
                    f"{result['held_out_count']:,} examples · decision threshold "
                    f"{result['threshold']:.0%}"
                )
                show_benchmark(result)
        st.info(
            "The URL results drop on the different collection. Email results are based on a small "
            "set that includes SMS-like text. Source labels and collection methods vary; use these "
            "scores to inform human review, not as a deployment guarantee."
        )

    st.markdown('<div class="cc-section-break"></div>', unsafe_allow_html=True)
    st.markdown("### Reading model scores")
    st.markdown(
        '<div class="cc-small-note">A model score is compared with the displayed threshold; '
        'it is not calibrated to real-world phishing prevalence. Email and URL models make '
        'independent predictions, and URL scores never change an email verdict. ClearCast does '
        'not open URLs or retrieve page content. A high score is a prompt for human review, '
        'not proof of malicious intent or a replacement for email security gateways, sandboxing, '
        'or human judgment.</div>',
        unsafe_allow_html=True,
    )
