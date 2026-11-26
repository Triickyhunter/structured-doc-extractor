import json
import os
import re
from typing import Any, Dict, List
from openai import OpenAI
from src.schemas import (
    DocumentExtractionResult,
    SafetyWarning,
    TechnicalSpecification,
)


def _extract_regex(pattern: str, text: str, default: str = "") -> str:
    match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
    return match.group(1).strip() if match else default


def _deterministic_fallback(raw_data: Dict[str, Any]) -> DocumentExtractionResult:
    full_text = raw_data.get("full_text", "")
    tables = raw_data.get("tables", [])

    # 1. Extraer especificaciones desde tablas detectadas por pdfplumber
    technical_specifications: List[TechnicalSpecification] = []
    for table in tables:
        if isinstance(table, list) and len(table) >= 2 and all(isinstance(c, str) for c in table):
            # En extractor.py clean_tables es una lista plana de filas
            if table[0].lower() not in {"property", "parameter"}:
                technical_specifications.append(
                    TechnicalSpecification(
                        parameter=table[0],
                        value=table[1],
                        unit=table[2] if len(table) > 2 and table[2] else None,
                    )
                )

    # 2. Si el PDF no tenía bordes de tabla, extraer propiedades clave-valor del texto
    if not technical_specifications:
        prop_match = re.search(
            r"Physical-Chemical Properties\s*\nProperty\s+Value\s*\n(.+)",
            full_text,
            re.IGNORECASE | re.DOTALL,
        )
        if prop_match:
            for line in prop_match.group(1).strip().splitlines():
                parts = re.split(r"\s{2,}", line.strip())
                if len(parts) == 1:
                    # Separar última palabra/valor si solo hay un espacio
                    tokens = line.strip().rsplit(" ", 2)
                    if len(tokens) >= 2:
                        technical_specifications.append(
                            TechnicalSpecification(
                                parameter=tokens[0],
                                value=" ".join(tokens[1:]),
                            )
                        )
                elif len(parts) >= 2:
                    technical_specifications.append(
                        TechnicalSpecification(
                            parameter=parts[0],
                            value=parts[1],
                            unit=parts[2] if len(parts) > 2 else None,
                        )
                    )

    # 3. Extraer advertencias de seguridad en el formato SafetyWarning(warning=...)
    safety_warnings: List[SafetyWarning] = []
    for line in full_text.splitlines():
        clean = line.strip()
        if clean.upper().startswith("SAFETY WARNING:") or clean.startswith("-"):
            msg = re.sub(r"^(SAFETY WARNING:\s*|-\s*)", "", clean, flags=re.IGNORECASE)
            if msg:
                safety_warnings.append(SafetyWarning(warning=msg))

    return DocumentExtractionResult(
        document_id=_extract_regex(r"Document ID:\s*(.+)", full_text, "DOC-UNKNOWN"),
        document_type=_extract_regex(r"Document Type:\s*(.+)", full_text, "Technical Spec"),
        product_or_material=_extract_regex(r"Product Name:\s*(.+)", full_text, "Unidentified Material"),
        supplier=_extract_regex(r"Supplier:\s*(.+)", full_text, "Unknown Supplier"),
        extraction_mode="deterministic_fallback",
        cas_or_sku=_extract_regex(r"CAS/SKU:\s*(.+)", full_text) or None,
        issue_date=_extract_regex(r"Issue Date:\s*(\d{4}-\d{2}-\d{2})", full_text) or None,
        technical_specifications=technical_specifications,
        safety_warnings=safety_warnings,
    )


def parse_to_schema(raw_data: Dict[str, Any], force_offline: bool = False) -> DocumentExtractionResult:
    if not force_offline and os.getenv("OFFLINE_MODE", "false").lower() != "true":
        try:
            client = OpenAI(
                base_url=os.getenv("LLM_BASE_URL", "http://localhost:11434/v1"),
                api_key=os.getenv("LLM_API_KEY", "ollama"),
                timeout=30.0,
            )
            model = os.getenv("LLM_MODEL", "qwen2.5-coder:7b")
            system_message = (
                "Extract structured data from the document text and return ONLY valid JSON "
                f"matching this JSON Schema: {json.dumps(DocumentExtractionResult.model_json_schema())}"
            )
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": json.dumps(raw_data, ensure_ascii=False)},
                ],
                temperature=0.0,
                response_format={"type": "json_object"},
            )
            parsed_data = json.loads(response.choices[0].message.content or "{}")
            parsed_data["extraction_mode"] = f"llm:{model}"
            return DocumentExtractionResult.model_validate(parsed_data)
        except Exception as e:
            print(f"LLM call failed, switching to deterministic fallback: {e}")

    return _deterministic_fallback(raw_data)