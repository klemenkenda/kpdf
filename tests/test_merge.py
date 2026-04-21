"""Pytest tests for PDF merge operation."""

from pathlib import Path

import pytest

pikepdf = pytest.importorskip("pikepdf")

from kpdf.operations.pdf_merger import merge_pdfs


def _create_blank_pdf(path: Path, pages: int) -> Path:
    doc = pikepdf.Pdf.new()
    for _ in range(pages):
        doc.add_blank_page(page_size=(612, 792))
    doc.save(path)
    doc.close()
    return path


def test_merge_multiple_pdfs(tmp_path: Path) -> None:
    doc1 = _create_blank_pdf(tmp_path / "document1.pdf", 2)
    doc2 = _create_blank_pdf(tmp_path / "document2.pdf", 3)
    doc3 = _create_blank_pdf(tmp_path / "document3.pdf", 1)
    output = tmp_path / "merged_output.pdf"

    result = merge_pdfs([str(doc1), str(doc2), str(doc3)], str(output))

    assert result == output
    assert output.exists()
    with pikepdf.Pdf.open(output) as merged_pdf:
        assert len(merged_pdf.pages) == 6
