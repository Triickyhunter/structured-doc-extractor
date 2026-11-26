import argparse
from pathlib import Path
from src.extractor import generate_sample_pdf, extract_pdf_content
from src.llm_parser import parse_to_schema
from src.schemas import DocumentExtractionResult
import openpyxl

def export_to_excel(result: DocumentExtractionResult, xlsx_path: Path):
    workbook = openpyxl.Workbook()
    summary_sheet = workbook.active
    summary_sheet.title = "Summary"

    summary_sheet.append([
        "document_id",
        "document_type",
        "product_or_material",
        "supplier",
        "cas_or_sku",
        "issue_date",
        "currency",
        "total_amount",
        "extraction_mode"
    ])

    summary_sheet.append([
        result.document_id,
        result.document_type,
        result.product_or_material,
        result.supplier,
        result.cas_or_sku,
        result.issue_date,
        result.currency,
        result.total_amount,
        result.extraction_mode
    ])

    specifications_sheet = workbook.create_sheet("Specifications")

    for spec in result.technical_specifications:
        specifications_sheet.append([spec.parameter, spec.value, spec.unit])

    safety_warnings_sheet = workbook.create_sheet("Safety_Warnings")

    for warning in result.safety_warnings:
        safety_warnings_sheet.append([warning.warning])
        
    workbook.save(xlsx_path)

def run_pipeline(pdf_path: Path, output_dir: Path, force_offline: bool = False) -> DocumentExtractionResult:
    if not pdf_path.exists() or force_offline:
        generate_sample_pdf(pdf_path)

    raw_data = extract_pdf_content(pdf_path)
    validated_result = parse_to_schema(raw_data, force_offline=force_offline)

    output_dir.mkdir(parents=True, exist_ok=True)

    json_path = output_dir / f"{pdf_path.stem}_extracted.json"
    xlsx_path = output_dir / f"{pdf_path.stem}_extracted.xlsx"

    json_path.write_text(validated_result.model_dump_json(indent=2), encoding="utf-8")  
    export_to_excel(validated_result, xlsx_path)

    return validated_result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PDF Extraction Pipeline")
    parser.add_argument("--pdf", type=Path, default=Path("data/sample_technical_spec.pdf"), help="Path to the PDF file")
    parser.add_argument("--out", type=Path, default=Path("output"), help="Output directory for results")
    parser.add_argument("--offline", action="store_true", help="Force offline mode, generate sample PDF if not exists")

    args = parser.parse_args()
    run_pipeline(args.pdf, args.out, args.offline)