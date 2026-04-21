"""Pytest tests for PDF text extraction."""

from pathlib import Path

import pytest

fitz = pytest.importorskip("fitz")

from kpdf.operations.pdf_extractor import extract_text_from_pdf


def _create_text_pdf(path: Path, text: str) -> Path:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), text)
    doc.save(path)
    doc.close()
    return path


def test_extract_text_to_string_and_file(tmp_path: Path) -> None:
    source = _create_text_pdf(tmp_path / "source.pdf", "Hello from pytest extract")
    output_txt = tmp_path / "extracted_text.txt"

    text = extract_text_from_pdf(str(source), str(output_txt))

    assert "Hello from pytest extract" in text
    assert output_txt.exists()
    assert output_txt.read_text(encoding="utf-8") == text
