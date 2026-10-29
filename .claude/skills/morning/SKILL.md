---
name: morning
description: Write today's morning newsletter from the fact pack, check it, show the maintainer, and (only after their approval) push it so it is sent to subscribers. Use when the maintainer types /morning or asks to write or send the morning newsletter.
---
The morning email is written by you from today's fact pack; a GitHub workflow sends it when the draft is pushed. Runbook: `docs/guidebook/06-operations-runbook.md` ("Newsletter"); rules: `docs/guidebook/07-editorial-policy.md` ("Morning newsletter").

1. Run `make morning-pack` (pulls the latest data, writes `newsletter/packs/<date>.md` and `newsletter/drafts/<date>.facts.json`; <date> is today in India). If `newsletter/drafts/<date>.md` already exists, ask before overwriting it.
2. Read the pack. Follow its rules exactly: use only the listed facts; write every number, date and period as its `{{token}}`, copied exactly; type no digit anywhere; no news, causes, forecasts or outside knowledge; 200-300 words, three to five short paragraphs with bold lead-ins; end with what is due today and coming up.
3. Write the email body to `newsletter/drafts/<date>.md`. A custom subject is optional, as front matter: `---\nsubject: "..."\n---` (tokens allowed, no digits).
4. Run `make morning-check`. If it reports problems, fix the draft and re-run until it passes.
5. Show the maintainer the preview (`newsletter/packs/<date>.preview.md`), with the subject line, and ask whether to send it. Sending emails every subscriber and cannot be undone.
6. Only after they say yes: `git add newsletter/drafts/<date>.md newsletter/drafts/<date>.facts.json`, commit ("newsletter: draft <date>", with the usual co-author line), and `git push`. The `newsletter-send` workflow checks it again and sends it. Tell them to watch Actions → newsletter-send.

Never edit `newsletter/drafts/<date>.facts.json` by hand, and never loosen the checker to make a draft pass.
