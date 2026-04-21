"""Merge multiple PDF documents into a single file."""

from pathlib import Path

import pikepdf

from kpdf.utils.error_handler import OperationError
from kpdf.utils.validators import ValidationError, require_existing_file


def merge_pdfs(input_paths: list[str], output_path: str) -> Path:
    """Merge PDF files in order and save a single output PDF."""
    if len(input_paths) < 2:
        raise OperationError("At least two PDF files are required for merge.")

    output = Path(output_path)
    if output.suffix.lower() != ".pdf":
        raise OperationError("Output file must have a .pdf extension.")

    try:
        merged = pikepdf.Pdf.new()
        for item in input_paths:
            source_path = require_existing_file(item)
            with pikepdf.Pdf.open(source_path) as source_pdf:
                merged.pages.extend(source_pdf.pages)

        output.parent.mkdir(parents=True, exist_ok=True)
        merged.save(output)
        merged.close()
        return output
    except (ValidationError, pikepdf.PdfError) as exc:
        raise OperationError(f"Failed to merge PDFs: {exc}") from exc
