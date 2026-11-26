# 📄 Structured Document Extractor (B2B Industrial & Chemical Pipeline)

Automated, hybrid document extraction pipeline designed for **B2B industrial, chemical, and logistics workflows**. Converts unstructured PDFs—such as Technical Data Sheets (TDS), Safety Data Sheets (SDS), and commercial specifications—into strictly validated **JSON** and multi-sheet **Excel (`.xlsx`)** deliverables ready for ERP, LIMS, or database ingestion.

---

## 💼 B2B Value Proposition

* **Zero-Hallucination Schema Enforcement:** Every extracted payload is validated against strict **Pydantic v2** data models (`DocumentExtractionResult`), guaranteeing consistent field types and non-empty critical identifiers before downstream export.
* **Hybrid AI + Deterministic Resilience:** Uses local LLMs via **Ollama** (`qwen2.5-coder:7b`) for complex layouts and automatically falls back to deterministic **regex + table parsing** (`pdfplumber`) in air-gapped environments or when no GPU/LLM endpoint is available.
* **ERP & Operations Ready:** Exports clean JSON alongside a formatted 3-tab Excel workbook (`Summary`, `Specifications`, `Safety_Warnings`).
* **100% Self-Hosted & Privacy-First:** Runs completely on-premises via Docker without sending proprietary supplier formulations or commercial documents to third-party cloud APIs.

---

## 🧠 Architecture Overview

```text
+-------------------+
|     Input PDF     |
+-------------------+
          |
          v
+-------------------+
|    pdfplumber     |  --> Deterministic text & table extraction
+-------------------+
          |
          v
+-------------------+
|    LLM / Regex    |  --> Local Ollama (OpenAI-compatible API)
|   Hybrid Parser   |      with automatic deterministic fallback
+-------------------+
          |
          v
+-------------------+
|    Pydantic v2    |  --> Strict schema & type validation
+-------------------+
          |
          v
+-------------------+
|  JSON & Excel     |  --> {stem}_extracted.json
|  Export (.xlsx)   |  --> {stem}_extracted.xlsx (3 sheets)
+-------------------+

🚀 Quickstart
Option A: Docker (Recommended)
Run the full extraction pipeline in an isolated container (automatically generates a sample industrial SDS PDF if data/ is empty):

Bash
# 1. Offline / deterministic mode (no LLM required)
docker compose run --rm -e OFFLINE_MODE=true extractor

# 2. Connected to local Ollama on the host machine
docker compose run --rm extractor
Option B: Local Python Environment
Bash
# 1. Create virtual environment and install dependencies
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Run automated test suite
PYTHONPATH=. pytest -v

# 3. Run the CLI pipeline (offline deterministic mode)
python -m src.main --pdf data/sample_technical_spec.pdf --out output --offline

📄 Sample Validated Output (_extracted.json)
JSON
{
  "document_id": "123456",
  "document_type": "SDS",
  "product_or_material": "Example Chemical",
  "supplier": "Example Supplier",
  "extraction_mode": "deterministic_fallback",
  "cas_or_sku": "123-45-6",
  "issue_date": "2023-10-01",
  "currency": null,
  "total_amount": null,
  "technical_specifications": [
    {
      "parameter": "Appearance",
      "value": "Clear liquid",
      "unit": null
    },
    {
      "parameter": "Boiling Point",
      "value": "100°C",
      "unit": null
    },
    {
      "parameter": "Density",
      "value": "1.2 g/cm³",
      "unit": null
    }
  ],
  "safety_warnings": [
    {
      "warning": "Handle with care. May cause harm."
    }
  ]
}
📁 Project Structure

structured-doc-extractor/
├── src/
│   ├── schemas.py        # Pydantic v2 data models & validators
│   ├── extractor.py      # Deterministic PDF reader & sample SDS generator
│   ├── llm_parser.py     # Ollama LLM client + regex fallback engine
│   └── main.py           # CLI entrypoint & multi-sheet Excel exporter
├── tests/
│   └── test_pipeline.py  # End-to-end pytest suite
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
📚 License
MIT License.


---

### 2. Crea `.dockerignore` y haz tu primer `git commit`

Ejecuta estos comandos en la terminal integrada de VS Code para evitar que Docker copie `.venv/` en futuros *builds* y registrar tu versión v1.0 en Git:

```bash
printf ".venv\n__pycache__\n.pytest_cache\n.git\noutput/*\n!output/.gitkeep\n" > .dockerignore
rmdir src/tests 2>/dev/null || true
git add .
git commit -m "feat: complete deterministic and LLM-assisted structured PDF extractor"
git status