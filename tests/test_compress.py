"""Pytest tests for PDF compression profiles."""

from pathlib import Path

import pytest

pikepdf = pytest.importorskip("pikepdf")

from kpdf.operations.pdf_compressor import compress_pdf


def _create_blank_pdf(path: Path, pages: int) -> Path:
	doc = pikepdf.Pdf.new()
	for _ in range(pages):
		doc.add_blank_page(page_size=(612, 792))
	doc.save(path)
	doc.close()
	return path


@pytest.mark.parametrize("profile", ["low", "medium", "high"])
def test_compress_profiles_preserve_pages(tmp_path: Path, profile: str) -> None:
	source = _create_blank_pdf(tmp_path / "source.pdf", 6)
	output = tmp_path / f"compressed_{profile}.pdf"

	result = compress_pdf(str(source), str(output), profile)

	assert result == output
	assert output.exists()
	with pikepdf.Pdf.open(output) as pdf:
		assert len(pdf.pages) == 6
