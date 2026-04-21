"""Extract text content from PDF files."""

from pathlib import Path

import fitz

from kpdf.utils.error_handler import OperationError
from kpdf.utils.validators import ValidationError, require_existing_file


def extract_text_from_pdf(input_path: str, output_path: str | None = None) -> str:
    """Extract text from all pages. Optionally save to a .txt file."""
    text_fragments: list[str] = []

    try:
        source_path = require_existing_file(input_path)
        document = fitz.open(source_path)
        try:
            for page in document:
                page_text = page.get_text("text")
                if page_text:
                    text_fragments.append(page_text)
        finally:
            document.close()

        extracted = "\n".join(fragment.strip() for fragment in text_fragments if fragment.strip())

        if output_path:
            output = Path(output_path)
            if output.suffix.lower() != ".txt":
                raise OperationError("Text output file must have a .txt extension.")
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(extracted, encoding="utf-8")

        return extracted
    except (ValidationError, fitz.FileDataError, RuntimeError, ValueError) as exc:
        raise OperationError(f"Failed to extract text: {exc}") from exc
