"""The morning newsletter: an AI-written summary of the latest data, emailed every day.

    python -m pipelines.newsletter.morning                     # today (IST): draft, check, send
    python -m pipelines.newsletter.morning --preview out.md    # write the email, send nothing
    python -m pipelines.newsletter.morning --no-ai --preview out.md   # the fallback template only

How it stays honest (07-editorial-policy.md, "Morning newsletter"):
  1. A ledger of facts is built from the stored series (registry/newsletter/morning.md
     `views`, the release calendar, what is new since yesterday). Each fact is a token such
     as {{cpi_headline_inflation.latest}} -> "5.54%".
  2. Claude writes the email using tokens only; it is told to use no other information and
     to type no digits. Model: site.config.yaml newsletter.llm_model.
  3. The briefing checker rejects any digit outside a token and any unknown token. One retry
     with the checker's complaints; if that fails too (or there is no ANTHROPIC_API_KEY),
     the fixed template in registry/newsletter/morning.md is sent instead.
  4. Tokens are replaced with the ledger's values, so every number in the email is a stored
     value, never one the model typed.
Sending: Buttondown (POST /v1/emails, status "about_to_send") when newsletter.enabled is true
and BUTTONDOWN_API_KEY is set; Buttondown's free plan covers one email a day to up to 100
subscribers. data/newsletter/sent.json stops a second send on the same date, and every email
is archived in data/newsletter/morning/<date>.md with its ledger.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date, timedelta

import httpx
import yaml

from pipelines.briefings.check import body_of, problems, render
from pipelines.briefings.draft import TEMPLATES as BRIEFING_TEMPLATES
from pipelines.briefings.ledger import Ledger, fmt_period
from pipelines.core import registry, store

TEMPLATE = store.ROOT / "registry" / "newsletter" / "morning.md"
SENT = store.ROOT / "data" / "newsletter" / "sent.json"
ARCHIVE = store.ROOT / "data" / "newsletter" / "morning"
API = "https://api.buttondown.com/v1/emails"
# Models that accept the server-side refusal fallback ("default" form).
FALLBACK_MODELS = {"claude-fable-5-1", "claude-opus-5-5", "claude-opus-5", "claude-sonnet-5-5"}

SYSTEM = """You write a short morning email about India's economy for economists and students.

You are given a list of facts. Each fact is a token in double braces followed by its value,
e.g. {{cpi_headline_inflation.latest}} = 5.54%.

Rules, all strict:
- Use only these facts. Do not add news, events, causes, forecasts, opinions about policy, or
  anything you know from elsewhere. Comparisons between the given facts are fine (for
  example, inflation above RBI's target, or a value higher than a year earlier).
- Write every number, date, percentage or period by copying its token exactly, braces
  included. Never type a digit (0-9) anywhere in your text, not even in a year or a heading.
  Words such as "ten-year" or "one" are fine. Values carry their sign; when your words
  already say "outflow", "deficit" or "fell by", use the token ending in .latest_abs.
- Choose what matters: lead with what is new since yesterday (listed for you), then markets,
  then two or three points from the wider picture (prices, growth and jobs, money, external,
  fiscal). Skip facts that add nothing.
- Format: Markdown, about 200 to 300 words, three to five short paragraphs, each starting
  with a bold lead-in such as **Markets.** End with what is due today and coming up, using
  the calendar tokens. No title, greeting or sign-off; output only the email body."""


def config() -> dict:
    return yaml.safe_load((store.ROOT / "site.config.yaml").read_text())


def template() -> tuple[dict, str]:
    text = TEMPLATE.read_text()
    return yaml.safe_load(text.split("---")[1]), text


def recent_releases(on: date, series_ids: list[str], days: int = 1, cap: int = 10) -> list[str]:
    """Headline series (the template's views) whose newest observation first appeared in the
    `days` days to `on`; daily and weekly series are left out (they update every day)."""
    since = (on - timedelta(days=days)).isoformat()
    out = []
    for sid in dict.fromkeys(series_ids):
        spec = registry.series(sid)
        df = store.load_series(sid)
        if df.empty or spec["frequency"] in ("D", "W"):
            continue
        last = df.sort_values("period").iloc[-1]
        if since <= str(last["vintage"]) <= on.isoformat():
            out.append(f"{spec['short_title']} ({fmt_period(str(last['period']), spec['frequency'])})")
    return out[:cap] + ([f"and {len(out) - cap} more"] if len(out) > cap else [])


def build_ledger(front: dict, on: date) -> tuple[Ledger, list[str]]:
    ledger = Ledger()
    ledger.add_calendar(on.isoformat())
    for view in front["views"]:
        sid, _, how = view.partition(":")
        ledger.add_view(sid, how or "level")
    ledger.add_constants(BRIEFING_TEMPLATES / "constants.yaml")
    new = recent_releases(on, [v.partition(":")[0] for v in front["views"]])
    ledger.facts["new.recent"] = "; ".join(new) if new else "no new monthly or quarterly data"
    ledger.facts["today.date"] = fmt_period(on.isoformat(), "D")
    return ledger, new


def ai_draft(ledger: Ledger, new: list[str], model: str, feedback: list[str] | None = None) -> tuple[str | None, dict]:
    """Ask Claude for a token-only draft. Returns (draft or None, usage info)."""
    import anthropic

    facts = "\n".join(f"{{{{{tok}}}}} = {val}" for tok, val in sorted(ledger.facts.items()))
    prompt = (f"New since yesterday: {'; '.join(new) if new else 'nothing new'}.\n\n"
              f"Facts:\n{facts}\n\nWrite today's email.")
    if feedback:
        prompt += ("\n\nYour previous draft was rejected by the checker for these reasons; fix "
                   "every one (copy tokens exactly, no digits outside tokens):\n- " + "\n- ".join(feedback))
    kwargs = dict(model=model, max_tokens=16000, system=SYSTEM,
                  messages=[{"role": "user", "content": prompt}])
    client = anthropic.Anthropic()
    if model in FALLBACK_MODELS:
        resp = client.beta.messages.create(**kwargs, betas=["server-side-fallback-2026-07-01"], fallbacks="default")
    else:
        resp = client.messages.create(**kwargs)
    usage = {"model": resp.model, "input_tokens": resp.usage.input_tokens, "output_tokens": resp.usage.output_tokens,
             "stop_reason": resp.stop_reason}
    if resp.stop_reason in ("refusal", "max_tokens"):
        return None, usage
    text = "".join(b.text for b in resp.content if b.type == "text").strip()
    return (text or None), usage


def compose(on: date, cfg: dict, use_ai: bool = True) -> dict:
    """{subject, body, drafted_by, usage, ledger} for the email of date `on`."""
    front, text = template()
    ledger, new = build_ledger(front, on)
    model = cfg["newsletter"].get("llm_model") or "claude-opus-5-5"
    draft, drafted_by, usage, issues = None, "template (no AI)", [], []
    if use_ai and os.environ.get("ANTHROPIC_API_KEY"):
        for attempt in range(2):
            try:
                candidate, info = ai_draft(ledger, new, model, issues or None)
            except Exception as e:                       # API trouble: fall back, never skip the email
                print(f"  AI draft failed: {type(e).__name__}: {e}")
                break
            usage.append(info)
            issues = problems(candidate, ledger.facts) if candidate else [f"no usable text ({info['stop_reason']})"]
            if not issues:
                draft, drafted_by = candidate, f"AI ({info['model']}), checked"
                break
            print(f"  attempt {attempt + 1} rejected: {issues[:3]}")
    if draft is None:
        draft = body_of(text).strip()
        tpl_issues = problems(draft, ledger.facts)
        if tpl_issues:
            raise ValueError(f"fallback template fails the checker: {tpl_issues}")
    site = cfg["site"]
    footer = (f"\n\n---\n\n*{site['name']}: {site['tagline']}.* Written by AI each morning from the data on "
              f"[{site['url'].split('//')[-1]}]({site['url']}) and checked automatically: every number above is "
              f"filled in from the stored series, not typed by the AI. Sources: [{site['url']}/data/]({site['url']}/data/). "
              f"Feedback: {cfg['contact'].get('feedback_email', '')}. "
              f"{' '.join(cfg['credit']['inspired_by_text'].split())}")
    if drafted_by.startswith("template"):
        footer = footer.replace("Written by AI each morning", "Generated each morning")
        footer = footer.replace(", not typed by the AI", "")
    return {"subject": render(front["subject"], ledger.facts), "body": render(draft, ledger.facts) + footer,
            "drafted_by": drafted_by, "usage": usage, "ledger": ledger}


def send(subject: str, body: str, key: str) -> str:
    # Buttondown asks for explicit confirmation the first time a key sends immediately.
    r = httpx.post(API, timeout=60, json={"subject": subject, "body": body, "status": "about_to_send"},
                   headers={"Authorization": f"Token {key}", "X-Buttondown-Live-Dangerously": "true"})
    r.raise_for_status()
    return r.json().get("id", "")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("--date", default=date.today().isoformat())
    ap.add_argument("--preview", help="write the email to this file; send nothing")
    ap.add_argument("--no-ai", action="store_true", help="use the fallback template only")
    args = ap.parse_args()
    on, cfg = date.fromisoformat(args.date), config()
    sent = json.loads(SENT.read_text()) if SENT.exists() else {}
    if not args.preview and on.isoformat() in sent:
        print(f"morning email for {on} already sent ({sent[on.isoformat()]['id']}); skipping")
        return 0
    email = compose(on, cfg, use_ai=not args.no_ai)
    for u in email["usage"]:
        print(f"  {u['model']}: {u['input_tokens']} input + {u['output_tokens']} output tokens ({u['stop_reason']})")
    print(f"  drafted by: {email['drafted_by']}")
    if args.preview:
        open(args.preview, "w").write(f"Subject: {email['subject']}\n\n{email['body']}\n")
        print(f"preview written to {args.preview}")
        return 0
    key = os.environ.get("BUTTONDOWN_API_KEY")
    if not (cfg["newsletter"].get("enabled") and key):
        print("newsletter disabled or BUTTONDOWN_API_KEY not set; nothing sent (use --preview to see the email)")
        return 0
    email_id = send(email["subject"], email["body"], key)
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    meta = {"subject": email["subject"], "date": on.isoformat(), "drafted_by": email["drafted_by"],
            "buttondown_id": email_id, "usage": email["usage"]}
    (ARCHIVE / f"{on}.md").write_text("---\n" + yaml.safe_dump(meta, sort_keys=False, allow_unicode=True)
                                      + "---\n" + email["body"] + "\n")
    (ARCHIVE / f"{on}.ledger.json").write_text(email["ledger"].dump())
    sent[on.isoformat()] = {"id": email_id, "subject": email["subject"], "drafted_by": email["drafted_by"]}
    SENT.parent.mkdir(parents=True, exist_ok=True)
    SENT.write_text(json.dumps(sent, indent=2))
    print(f"sent: {email['subject']} ({email_id})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
