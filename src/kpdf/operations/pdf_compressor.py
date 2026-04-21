"""PDF compression helpers based on pikepdf save options."""

from pathlib import Path

import pikepdf

from kpdf.utils.error_handler import OperationError
from kpdf.utils.validators import ValidationError, require_existing_file

COMPRESSION_PROFILES = {"low", "medium", "high"}


def compress_pdf(input_path: str, output_path: str, profile: str = "medium") -> Path:
    """Compress a PDF with practical profile-based options."""
    normalized_profile = profile.lower().strip()
    if normalized_profile not in COMPRESSION_PROFILES:
        raise OperationError("Compression profile must be low, medium, or high.")

    output = Path(output_path)
    if output.suffix.lower() != ".pdf":
        raise OperationError("Output file must have a .pdf extension.")

    try:
        source_path = require_existing_file(input_path)
        with pikepdf.Pdf.open(source_path) as source_pdf:
            save_kwargs: dict[str, object] = {"compress_streams": True}
            if normalized_profile == "low":
                save_kwargs["object_stream_mode"] = pikepdf.ObjectStreamMode.disable
            if normalized_profile == "medium":
                save_kwargs["object_stream_mode"] = pikepdf.ObjectStreamMode.generate
            if normalized_profile == "high":
                save_kwargs["object_stream_mode"] = pikepdf.ObjectStreamMode.generate
                save_kwargs["linearize"] = True

            output.parent.mkdir(parents=True, exist_ok=True)
            source_pdf.save(output, **save_kwargs)
            return output
    except (ValidationError, pikepdf.PdfError) as exc:
        raise OperationError(f"Failed to compress PDF: {exc}") from exc
