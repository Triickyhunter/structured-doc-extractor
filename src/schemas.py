from pydantic import BaseModel, Field, validator
from typing import List, Optional


class TechnicalSpecification(BaseModel):
    parameter: str
    value: str
    unit: Optional[str] = Field(None, description='Unit of measurement for the parameter')

class SafetyWarning(BaseModel):
    warning: str


class DocumentExtractionResult(BaseModel):
    document_id: str
    document_type: str
    product_or_material: str
    supplier: str
    extraction_mode: str
    cas_or_sku: Optional[str] = Field(None, description='CAS number or SKU code')
    issue_date: Optional[str] = Field(None, description='Issue date of the document')
    currency: Optional[str] = Field(None, description='Currency used in the document')
    total_amount: Optional[float] = Field(None, description='Total amount of the document')
    technical_specifications: List[TechnicalSpecification] = Field(default=[], description='Technical specifications of the product or material')
    safety_warnings: List[SafetyWarning] = Field(default=[], description='Safety warnings related to the product or material')

    @validator('*', pre=True)
    def validate_non_empty_strings(cls, value):
        if isinstance(value, str) and not value.strip():
            raise ValueError('Strings cannot be empty')
        return value

    @validator('document_id')
    def document_id_not_empty(cls, value):
        if not value:
            raise ValueError('document_id cannot be empty')
        return value

    @validator('document_type')
    def document_type_not_empty(cls, value):
        if not value:
            raise ValueError('document_type cannot be empty')
        return value

    @validator('product_or_material')
    def product_or_material_not_empty(cls, value):
        if not value:
            raise ValueError('product_or_material cannot be empty')
        return value

    @validator('supplier')
    def supplier_not_empty(cls, value):
        if not value:
            raise ValueError('supplier cannot be empty')
        return value

    @validator('extraction_mode')
    def extraction_mode_not_empty(cls, value):
        if not value:
            raise ValueError('extraction_mode cannot be empty')
        return value