# Pipeline Walkthrough

## Task 1 — Scraping
1. Define the five public target pages and the fields requested for each.
2. Fetch each page with a descriptive user agent and bounded timeout.
3. Parse HTML using BeautifulSoup and conservative selectors / text patterns.
4. Normalize results into a consistent JSON shape: `source`, `url`, `scraped_at`, `items`, and `errors`.
5. Write one JSON file per site. If the site blocks access or markup differs, store a diagnostic instead of fabricating results.
6. Validate the output JSON and review fields manually because commercial sites frequently change markup and may limit automated access.

## Task 2 — Context Handling
1. Read the internal dossier as the source of truth.
2. Cross-reference incident costs and severity weights rather than relying on a single table.
3. Read the scanned Appendix B memo image for the SentinelWatch renewal date and approval authority.
4. Calculate weighted cost only for incidents with the specified root cause.
5. Preserve source terminology and avoid inferring details not supported by the dossier.

## Task 3 — Local LLM Security
1. Keep Ollama bound to localhost and call it only from the Python API.
2. Require a bearer token before any inference request.
3. Validate request structure and input size; reject empty or oversized prompts.
4. Apply per-client rate limiting and a bounded generation length / timeout.
5. Use a fixed server-side system prompt, never concatenate user text as privileged instructions, and instruct the model to treat user-provided content as untrusted.
6. Return only the model answer, not internal prompts or debug details.
7. Add health and readiness checks that do not reveal secrets. In production, add centralized secret storage, audit logging, stronger distributed rate limiting, and adversarial tests.
