# Technical Assessment

This repository is organized into the three requested tasks.

## Requirements
- Python 3.11+
- For scraping: `pip install -r task1_scraping/requirements.txt`
- For context questions: `pip install -r task2_context/requirements.txt`
- For local LLM security API: `pip install -r task3_llm_security/requirements.txt`
- Ollama installed locally, with a model pulled (for example `ollama pull llama3.2`).

## Run Task 1 — Scraping
```bash
cd task1_scraping
pip install -r requirements.txt
python scrape_all.py
```
The script writes one JSON file per target into `output/`. Live websites may block automated requests, change their markup, require login, or restrict automated access. The implementation uses public pages only and records a clear error in the site's JSON if a page cannot be accessed or the expected fields cannot be extracted. Do not bypass CAPTCHAs, access controls, or site restrictions.

## Run Task 2 — Context Handling
```bash
cd task2_context
pip install -r requirements.txt
python answer_questions.py
```
Answers are based only on the supplied dossier and scanned Appendix B memo. See `answers.json`.

## Run Task 3 — Local LLM Security
Start Ollama and ensure the model is available:
```bash
ollama pull llama3.2
ollama serve
```
In another terminal:
```bash
cd task3_llm_security
python -m venv .venv
# activate the environment, then:
pip install -r requirements.txt
uvicorn app:app --host 127.0.0.1 --port 8000
```
API docs: `http://127.0.0.1:8000/docs`

The API requires a bearer token, enforces request-size and rate limits, does not expose system prompts, and treats user input as untrusted. This is a local assessment scaffold, not a substitute for production secrets management, monitoring, or security review.
