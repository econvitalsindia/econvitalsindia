// POST /api/subscribe: newsletter sign-up, run by Cloudflare Pages Functions.
// The signup box posts here instead of to Buttondown's embed form (which blocks framing and
// drops sign-ups that don't come from a top-level page). This adds the address through
// Buttondown's API as "unactivated", so Buttondown sends its usual confirmation email
// (double opt-in), and passes the reader's IP so Buttondown's spam checks still apply.
// BUTTONDOWN_API_KEY is a Pages secret set by the maintainer in the Cloudflare dashboard
// (Workers & Pages -> econvitalsindia -> Settings -> Variables and Secrets).
// Responses are JSON: {ok: true, status: "created" | "exists"} or {ok: false, error}.

const json = (body, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json", "cache-control": "no-store" } });

export async function onRequestPost({ request, env }) {
  let form;
  try {
    form = await request.formData();
  } catch {
    return json({ ok: false, error: "bad request" }, 400);
  }
  // Honeypot: people never see or fill this field; bots often do.
  if (form.get("website")) return json({ ok: true, status: "created" });
  const email = String(form.get("email") || "").trim();
  if (email.length > 254 || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) {
    return json({ ok: false, error: "That doesn't look like an email address." }, 400);
  }
  if (!env.BUTTONDOWN_API_KEY) return json({ ok: false, error: "Sign-ups are not configured yet." }, 503);

  const r = await fetch("https://api.buttondown.com/v1/subscribers", {
    method: "POST",
    headers: { Authorization: `Token ${env.BUTTONDOWN_API_KEY}`, "Content-Type": "application/json" },
    body: JSON.stringify({
      email_address: email,
      type: "unactivated",
      ip_address: request.headers.get("CF-Connecting-IP") || undefined,
    }),
  });
  if (r.status === 201) return json({ ok: true, status: "created" });
  const text = await r.text();
  // Buttondown answers 400 when the address is already on the list (pending or confirmed).
  if (r.status === 400 && /already|exist|collision|subscribed/i.test(text)) return json({ ok: true, status: "exists" });
  if (r.status === 429) return json({ ok: false, error: "Too many sign-ups just now; please try again later." }, 429);
  console.log(`buttondown ${r.status}: ${text.slice(0, 300)}`);
  let code = "", detail = "";
  try { ({ code = "", detail = "" } = JSON.parse(text)); } catch { detail = text.slice(0, 200); }
  return json({ ok: false, error: "The sign-up service didn't accept that address.", provider_status: r.status,
                provider_code: code, provider_detail: String(detail).slice(0, 300) }, 502);
}
