# Technical Requirements — Senior Scam Checker MVP

_Last updated: 2025-09-04_

## 1) Goal & Scope
Deliver a minimal, reliable web app that:
- Publishes **Top 10 Scams** educational content (senior‑friendly).
- Provides a **guided “Check if this is a scam” form** whose answers are analyzed by an LLM behind a conservative rules gate.
- Demonstrates an **agentic workflow** (classification + next‑step guidance), suitable for portfolio demos.

Non‑goals: incident case management, user accounts, attachments upload, or third‑party data sharing.

---

## 2) Architecture Overview
**Frontend:** Static site (HTML/CSS/JS) served by Replit’s web server.  
**Backend:** Python + Flask (single `app.py`) for API endpoints.  
**LLM Provider:** OpenAI (Completions/Responses API).  
**Data:** No database for MVP; content in Markdown; configuration via env vars and JSON files.

```
Browser
  ├─ / (Landing)
  ├─ /learn (Top 10 Scams content, Markdown-rendered)
  └─ /check (Guided form)
           │
           ▼
      Flask API
      ├─ POST /api/check-scam     (validate + analyze)
      ├─ GET  /api/health         (liveness)
      └─ GET  /api/version        (static version info)
           │
           ▼
       OpenAI API  (guarded by rules + prompt template)
           │
           ▼
     Response JSON → UI result panel
```

Latency targets:
- Static pages TTFB < 1s on p95.
- `/api/check-scam` p95 ≤ 3s, hard timeout 8s, graceful fallback message if exceeded.

---

## 3) Security, Privacy & Safety
- **No PII storage.** Do not persist form text; process in‑memory only.
- **Sanitize inputs.** Length limit (2,000 chars), strip HTML, reject URLs optionally.
- **Rate limiting.** 20 req/min/IP (simple token bucket in memory).
- **Secrets.** `OPENAI_API_KEY` via Replit Secrets; never commit to repo.
- **Transport.** HTTPS by default on Replit.
- **Safety copy.** Prominent disclaimer: “Educational triage, not final determination.”
- **Escalation.** Always provide official contacts (Scamwatch, IDCARE) in outputs.
- **Observability.** Log only event metadata (timestamp, category, red‑flag counts, latency). No user content in logs.

---

## 4) Accessibility Requirements (WCAG 2.2 AA)
- Base font >= 18px; line-height 1.6; hit targets ≥ 44×44px.
- High contrast color palette; never rely on color alone for meaning.
- Logical heading order, landmarks (header/nav/main/footer).
- Keyboard‑only navigation; visible focus rings.
- `aria-live="polite"` for result messages; labels + descriptions on all inputs.
- Text‑to‑speech friendly copy; avoid nested accordions.
- “Print view” CSS for one‑page checklists.

---

## 5) Pages & UI Components
### 5.1 Landing `/`
- Hero: “Spot scams. Stay safe.”
- Two CTAs: **Learn** and **Check a message**.
- “Emergency steps” banner with key hotlines.

### 5.2 Learn `/learn`
- Render `top_10_scams_final.md` into HTML (server or client).
- Each scam uses consistent blocks: Summary, How it works, Red Flags, What to Do, Quick Script, Report & Help.
- Print button (generates print‑optimized page).

### 5.3 Check `/check`
- Stepper form (3 steps):
  1) **Channel:** Email, SMS, Phone call, Social, Other.
  2) **Behavior:** Ask money now, ask personal info, pressure urgency, claims government/bank, remote access, prize/lottery, “relative in trouble,” charity/disaster, investment, contractor/repair.
  3) **Details (optional):** free text up to 500 chars.
- Submit calls `/api/check-scam`, displays verdict: Low/Medium/High Risk + 3 next actions + referral links.
- Copy button for advice; “Call a trusted contact” button (configurable tel: link).

---

## 6) API Design
### 6.1 POST `/api/check-scam`
**Request (JSON):**
```json
{
  "channel": "sms|email|phone|social|other",
  "flags": ["money_now","personal_info","urgency","gov_bank","remote_access","prize","relative_trouble","charity","investment","contractor"],
  "details": "optional short text (<=500)",
  "locale": "en-AU"
}
```

**Response (JSON):**
```json
{
  "risk_level": "low|medium|high",
  "reasons": ["short, plain reasons"],
  "next_steps": [
    "Do not reply or click links.",
    "Contact your bank using the number on your card.",
    "Report to Scamwatch and IDCARE."
  ],
  "resources": [
    {"label": "Scamwatch (ACCC)", "url": "https://www.scamwatch.gov.au"},
    {"label": "IDCARE (AU)", "tel": "1800 595 160"}
  ],
  "meta": {"latency_ms": 1234, "model": "gpt-3.5-turbo", "version": "2025.09.03"}
}
```

**Validation rules:**
- `channel` required; `flags` non-empty.
- `details` length ≤ 500; strip HTML.
- Reject if request body > 4 KB.

### 6.2 GET `/api/health`
- Returns `{"status":"ok"}`.

### 6.3 GET `/api/version`
- Returns `{ "version": "YYYY.MM.DD", "commit": "short_sha" }` (manually updated).

---

## 7) Server Logic (Pseudocode)
```python
# app.py
from flask import Flask, request, jsonify
import os, time
import tiktoken  # optional; for token budgeting
import openai
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

openai.api_key = os.environ["OPENAI_API_KEY"]

ALLOWED_FLAGS = {...}  # same as API doc
TIMEOUT_S = 8

def rules_engine(channel, flags, details):
    score = 0
    reasons = []
    # deterministic signals
    if "gov_bank" in flags: score += 3; reasons.append("Pretends to be a bank/government")
    if "money_now" in flags: score += 3; reasons.append("Asks for money urgently")
    if "personal_info" in flags: score += 2; reasons.append("Asks for personal details")
    if "remote_access" in flags: score += 4; reasons.append("Requests remote access")
    if "prize" in flags: score += 2; reasons.append("Prize/lottery with fees")
    if "relative_trouble" in flags: score += 3; reasons.append("Relative-in-trouble story")
    if "investment" in flags: score += 2; reasons.append("Unrealistic investment returns")
    if "contractor" in flags: score += 1; reasons.append("Unsolicited repair offer")
    risk = "low" if score <=2 else "medium" if score<=5 else "high"
    return risk, reasons

@app.post("/api/check-scam")
def check_scam():
    t0 = time.time()
    data = request.get_json(force=True, silent=True) or {}
    # validate
    # ... (return 400 on invalid)
    risk, reasons = rules_engine(data["channel"], data["flags"], data.get("details",""))
    # short-circuit: high risk → we can answer without LLM
    if risk == "high":
        resp = {
          "risk_level": "high",
          "reasons": reasons,
          "next_steps": [
            "Stop contact and do not send money.",
            "Call your bank using the number on your card.",
            "Report to Scamwatch and IDCARE."
          ],
          "resources":[
            {"label":"Scamwatch (ACCC)", "url":"https://www.scamwatch.gov.au"},
            {"label":"IDCARE (AU)", "tel":"1800 595 160"}
          ],
          "meta":{"latency_ms": int((time.time()-t0)*1000), "model": None, "version": "2025.09.03"}
        }
        return jsonify(resp)

    # otherwise call LLM with conservative prompt
    prompt = build_prompt(data, risk, reasons)
    try:
        with time_limit(TIMEOUT_S):
            result = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role":"system","content":SYSTEM_PROMPT},
                          {"role":"user","content":prompt}],
                temperature=0.1,
                max_tokens=400
            )
        advice = parse_llm(result)
    except Exception:
        advice = fallback_advice(risk, reasons)

    resp = advice
    resp["meta"] = {"latency_ms": int((time.time()-t0)*1000), "model":"gpt-3.5-turbo", "version":"2025.09.03"}
    return jsonify(resp)
```

**System prompt (summary):**
- Role: safety triage assistant for seniors in Australia.
- Style: plain English, short sentences, action-first.
- Never request money or personal info; never guarantee outcomes.
- Always propose 3 concrete next steps + official resources.
- If uncertain, choose safer path and escalate.

---

## 8) Content & Configuration
- `content/top_10_scams_final.md` → rendered on `/learn`.
- `config/resources.au.json` → phone numbers and URLs for AU.
- `config/flags.json` → available red‑flag options and labels.
- `config/feature_flags.json` → enable/disable LLM, show debug panel in dev.

---

## 9) Performance
- HTTP keep‑alive, gzip on static assets.
- Cache static content with long max‑age; bust via version hash.
- Debounce form submits; block double‑clicks.
- Preload core CSS; avoid large JS frameworks for MVP (< 50 KB JS).

---

## 10) Testing
- **Unit:** rules_engine scoring; validators; prompt builder.
- **Contract:** JSON schema tests for `/api/check-scam` with happy/sad paths.
- **Accessibility:** axe-core smoke test; keyboard‑only flow.
- **Prompt eval:** golden files for 6 archetype cases (tech support, gov impersonation, “Hi Mum” SMS, prize, investment, contractor).
- **Load:** 10 RPS for 1 minute without failures on Replit.

---

## 11) Deployment on Replit
1. New Replit (Python Flask template).  
2. Add files: `app.py`, `static/`, `templates/`, `content/top_10_scams_final.md`, `config/*.json`.  
3. Set Secrets: `OPENAI_API_KEY`.  
4. Configure Run command:
   ```bash
   python app.py
   ```
5. Verify health at `/api/health`, version at `/api/version`.  
6. Smoke test `/check` end‑to‑end.

---

## 12) Risks & Mitigations
- **LLM outage or slowness:** rules_engine short‑circuit + cached fallback advice.  
- **Hallucinations:** temperature=0.1; deterministic prompt; fixed next‑steps list.  
- **Over‑collection of data:** strict limits; no logs of content; privacy copy in footer.  
- **User confusion:** scripts + large buttons; consistent layout; print view.  
- **Extension conflicts (future):** namespaced CSS; no global keybindings.

---

## 13) Nice‑to‑Have (v1.1+)
- Simple telemetry dashboard (anonymous counts).  
- “Trusted contact” configuration (tel link).  
- Lightweight i18n; en‑AU → en‑US.  
- Attachment OCR for screenshots (with on‑device redaction).

---

## 14) Repository Layout
```
/app.py
/templates/
  base.html
  index.html
  learn.html
  check.html
/static/
  css/styles.css
  js/app.js
/content/
  top_10_scams_final.md
/config/
  resources.au.json
  flags.json
  feature_flags.json
/tests/
  test_rules.py
  test_api_contract.py
README.md
```

---

## 15) Sample Minimal Flask Endpoint (reference)
```python
from flask import Flask, request, jsonify
import os, openai

app = Flask(__name__)
openai.api_key = os.environ.get("OPENAI_API_KEY")

@app.get("/api/health")
def health():
    return jsonify({"status":"ok"})

@app.post("/api/check-scam")
def check_scam():
    data = request.get_json() or {}
    channel = data.get("channel")
    flags = data.get("flags", [])
    details = (data.get("details") or "")[:500]

    # simple validation
    if channel not in {"sms","email","phone","social","other"} or not flags:
        return jsonify({"error":"invalid input"}), 400

    # simple rules first
    risk = "high" if "remote_access" in flags or "gov_bank" in flags and "money_now" in flags else "medium"

    # optional LLM call (pseudo)
    # resp = openai.ChatCompletion.create(...)

    return jsonify({
        "risk_level": risk,
        "reasons": ["Heuristic signals only (MVP)"],
        "next_steps": ["Do not engage further.", "Contact your bank.", "Report to Scamwatch."],
        "resources":[
            {"label":"Scamwatch (ACCC)", "url":"https://www.scamwatch.gov.au"},
            {"label":"IDCARE (AU)", "tel":"1800 595 160"}
        ]
    })
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
```
