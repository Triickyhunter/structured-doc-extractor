from pathlib import Path
import pdfplumber
from fpdf import FPDF
from typing import Dict, Union

def extract_pdf_content(pdf_path: Union[str, Path]) -> Dict[str, Union[str, list]]:
    with pdfplumber.open(pdf_path) as pdf:
        file_name = Path(pdf_path).name
        full_text = ""
        tables = []

        for page in pdf.pages:
            full_text += page.extract_text() + "\n"
            tables.extend(page.extract_tables())

        # Clean up tables
        clean_tables = []
        for table in tables:
            clean_table = []
            for row in table:
                clean_row = [cell.strip() for cell in row if cell.strip()]
                if clean_row:
                    clean_tables.append(clean_row)

        return {
            "file_name": file_name,
            "full_text": full_text,
            "tables": clean_tables
        }

def generate_sample_pdf(output_path: Union[str, Path]) -> Path:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Add title and metadata
    pdf.cell(200, 10, txt="Sample Safety Data Sheet", ln=True, align='C')
    pdf.cell(200, 10, txt="Document ID: 123456", ln=True)
    pdf.cell(200, 10, txt="Document Type: SDS", ln=True)
    pdf.cell(200, 10, txt="Product Name: Example Chemical", ln=True)
    pdf.cell(200, 10, txt="Supplier: Example Supplier", ln=True)
    pdf.cell(200, 10, txt="CAS/SKU: 123-45-6", ln=True)
    pdf.cell(200, 10, txt="Issue Date: 2023-10-01", ln=True)

    # Add safety warnings
    pdf.cell(200, 10, txt="SAFETY WARNING: Handle with care. May cause harm.", ln=True)
    pdf.cell(200, 10, txt="Keep out of reach of children. Use only as directed.", ln=True)

    # Add physical-chemical properties table
    pdf.ln()
    pdf.cell(200, 10, txt="Physical-Chemical Properties", ln=True)
    pdf.cell(100, 10, txt="Property", ln=False)
    pdf.cell(100, 10, txt="Value", ln=True)
    pdf.cell(100, 10, txt="Appearance", ln=False)
    pdf.cell(100, 10, txt="Clear liquid", ln=True)
    pdf.cell(100, 10, txt="Boiling Point", ln=False)
    pdf.cell(100, 10, txt="100°C", ln=True)
    pdf.cell(100, 10, txt="Density", ln=False)
    pdf.cell(100, 10, txt="1.2 g/cm³", ln=True)

    pdf.output(output_path)
    return Path(output_path)