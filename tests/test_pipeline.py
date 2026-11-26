import pytest
from pathlib import Path
from src.main import generate_sample_pdf, run_pipeline

def test_offline_pipeline_end_to_end(tmp_path):
    sample_pdf = tmp_path / "sample.pdf"
    out_dir = tmp_path / "output"
    sample_pdf.write_text("Sample PDF content")

    result = run_pipeline(sample_pdf, out_dir, force_offline=True)

    assert result.document_id == "123456"
    assert result.extraction_mode == "deterministic_fallback"
    assert len(result.technical_specifications) > 0

    extracted_json_path = out_dir / f"{sample_pdf.stem}_extracted.json"
    extracted_xlsx_path = out_dir / f"{sample_pdf.stem}_extracted.xlsx"

    assert extracted_json_path.exists() and extracted_json_path.stat().st_size > 0
    assert extracted_xlsx_path.exists() and extracted_xlsx_path.stat().st_size > 0

def test_auto_sample_generation_when_pdf_missing(tmp_path):
    non_existent_pdf = tmp_path / "non_existent.pdf"
    out_dir = tmp_path / "output"

    result = run_pipeline(non_existent_pdf, out_dir, force_offline=True)

    assert result.document_id == "123456"
    assert result.extraction_mode == "deterministic_fallback"
    assert len(result.technical_specifications) > 0

    extracted_json_path = out_dir / f"{non_existent_pdf.stem}_extracted.json"
    extracted_xlsx_path = out_dir / f"{non_existent_pdf.stem}_extracted.xlsx"

    assert non_existent_pdf.exists() and non_existent_pdf.stat().st_size > 0
    assert extracted_json_path.exists() and extracted_json_path.stat().st_size > 0
    assert extracted_xlsx_path.exists() and extracted_xlsx_path.stat().st_size > 0