"""Rotate pages in a PDF document."""

from pathlib import Path

import pikepdf

from kpdf.utils.error_handler import OperationError
from kpdf.utils.validators import ValidationError, require_existing_file

ALLOWED_ANGLES = {90, 180, 270}


def rotate_pdf(input_path: str, output_path: str, angle: int) -> Path:
    """Rotate all pages in a PDF by one of the allowed angles."""
    if angle not in ALLOWED_ANGLES:
        raise OperationError("Angle must be one of 90, 180, or 270 degrees.")

    output = Path(output_path)
    if output.suffix.lower() != ".pdf":
        raise OperationError("Output file must have a .pdf extension.")

    try:
        source_path = require_existing_file(input_path)
        with pikepdf.Pdf.open(source_path) as source_pdf:
            for page in source_pdf.pages:
                current_rotation = int(page.get("/Rotate", 0))
                page.Rotate = (current_rotation + angle) % 360

            output.parent.mkdir(parents=True, exist_ok=True)
            source_pdf.save(output)
            return output
    except (ValidationError, pikepdf.PdfError, ValueError, TypeError) as exc:
        raise OperationError(f"Failed to rotate PDF: {exc}") from exc
