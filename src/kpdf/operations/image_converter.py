"""Convert image files into a PDF document."""

from pathlib import Path

import img2pdf

from kpdf.utils.error_handler import OperationError
from kpdf.utils.validators import ValidationError, require_existing_file

SUPPORTED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}


def images_to_pdf(image_paths: list[str], output_path: str) -> Path:
    """Convert ordered image inputs to a single PDF output."""
    if not image_paths:
        raise OperationError("At least one image is required.")

    output = Path(output_path)
    if output.suffix.lower() != ".pdf":
        raise OperationError("Output file must have a .pdf extension.")

    try:
        ordered_inputs: list[str] = []
        for image_path in image_paths:
            candidate = require_existing_file(image_path)
            if candidate.suffix.lower() not in SUPPORTED_IMAGE_EXTENSIONS:
                raise OperationError(f"Unsupported image type: {candidate.suffix}")
            ordered_inputs.append(str(candidate))

        pdf_bytes = img2pdf.convert(ordered_inputs)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(pdf_bytes)
        return output
    except (ValidationError, img2pdf.ImageOpenError, img2pdf.AlphaChannelError) as exc:
        raise OperationError(f"Failed to convert images to PDF: {exc}") from exc
