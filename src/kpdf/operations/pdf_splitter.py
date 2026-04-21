"""Split a PDF document by page ranges."""

from pathlib import Path

import pikepdf

from kpdf.utils.error_handler import OperationError
from kpdf.utils.validators import ValidationError, require_existing_file


def parse_page_ranges(page_ranges: str, max_pages: int) -> list[int]:
    """Parse a range expression like '1-3,5,8-9' into sorted unique pages."""
    if not page_ranges.strip():
        raise OperationError("Page range cannot be empty.")

    pages: set[int] = set()
    chunks = [chunk.strip() for chunk in page_ranges.split(",") if chunk.strip()]

    for chunk in chunks:
        if "-" in chunk:
            start_text, end_text = [item.strip() for item in chunk.split("-", maxsplit=1)]
            if not start_text.isdigit() or not end_text.isdigit():
                raise OperationError(f"Invalid range segment: {chunk}")
            start = int(start_text)
            end = int(end_text)
            if start > end:
                raise OperationError(f"Range start is greater than end: {chunk}")
            for page_num in range(start, end + 1):
                if page_num < 1 or page_num > max_pages:
                    raise OperationError(f"Page out of bounds: {page_num}")
                pages.add(page_num)
        else:
            if not chunk.isdigit():
                raise OperationError(f"Invalid page number: {chunk}")
            page_num = int(chunk)
            if page_num < 1 or page_num > max_pages:
                raise OperationError(f"Page out of bounds: {page_num}")
            pages.add(page_num)

    if not pages:
        raise OperationError("No pages selected for split.")

    return sorted(pages)


def split_pdf(input_path: str, output_path: str, page_ranges: str) -> Path:
    """Split a PDF using page ranges and write selected pages to output."""
    output = Path(output_path)
    if output.suffix.lower() != ".pdf":
        raise OperationError("Output file must have a .pdf extension.")

    try:
        source_path = require_existing_file(input_path)
        with pikepdf.Pdf.open(source_path) as source_pdf:
            selected_pages = parse_page_ranges(page_ranges, len(source_pdf.pages))

            result_pdf = pikepdf.Pdf.new()
            for page_num in selected_pages:
                result_pdf.pages.append(source_pdf.pages[page_num - 1])

            output.parent.mkdir(parents=True, exist_ok=True)
            result_pdf.save(output)
            result_pdf.close()
            return output
    except (ValidationError, pikepdf.PdfError) as exc:
        raise OperationError(f"Failed to split PDF: {exc}") from exc
