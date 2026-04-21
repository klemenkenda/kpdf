"""Pytest tests for PDF rotate operation."""

from pathlib import Path

import pytest

pikepdf = pytest.importorskip("pikepdf")

from kpdf.operations.pdf_rotator import rotate_pdf


def _create_blank_pdf(path: Path, pages: int) -> Path:
	doc = pikepdf.Pdf.new()
	for _ in range(pages):
		doc.add_blank_page(page_size=(612, 792))
	doc.save(path)
	doc.close()
	return path


@pytest.mark.parametrize("angle", [90, 180, 270])
def test_rotate_pdf_angles(tmp_path: Path, angle: int) -> None:
	source = _create_blank_pdf(tmp_path / "source.pdf", 2)
	output = tmp_path / f"rotated_{angle}.pdf"

	result = rotate_pdf(str(source), str(output), angle)

	assert result == output
	with pikepdf.Pdf.open(result) as pdf:
		assert len(pdf.pages) == 2
