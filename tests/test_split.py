"""Pytest tests for PDF split operation."""

from pathlib import Path

import pytest

pikepdf = pytest.importorskip("pikepdf")

from kpdf.operations.pdf_splitter import split_pdf


def _create_blank_pdf(path: Path, pages: int) -> Path:
	doc = pikepdf.Pdf.new()
	for _ in range(pages):
		doc.add_blank_page(page_size=(612, 792))
	doc.save(path)
	doc.close()
	return path


def test_split_contiguous_range(tmp_path: Path) -> None:
	source = _create_blank_pdf(tmp_path / "source.pdf", 6)
	output = tmp_path / "split_1_3.pdf"
	result = split_pdf(str(source), str(output), "1-3")

	assert result == output
	with pikepdf.Pdf.open(result) as pdf:
		assert len(pdf.pages) == 3


def test_split_non_contiguous_range(tmp_path: Path) -> None:
	source = _create_blank_pdf(tmp_path / "source.pdf", 6)
	output = tmp_path / "split_2_4_6.pdf"
	result = split_pdf(str(source), str(output), "2,4,6")

	assert result == output
	with pikepdf.Pdf.open(result) as pdf:
		assert len(pdf.pages) == 3
