"""Pytest tests for image-to-PDF conversion."""

from pathlib import Path

import pytest

pikepdf = pytest.importorskip("pikepdf")
PIL = pytest.importorskip("PIL.Image")

from kpdf.operations.image_converter import images_to_pdf


def _create_image(path: Path, color: tuple[int, int, int]) -> Path:
	image = PIL.new("RGB", (120, 120), color=color)
	image.save(path)
	return path


def test_convert_png_images_to_pdf(tmp_path: Path) -> None:
	img1 = _create_image(tmp_path / "image1.png", (255, 0, 0))
	img2 = _create_image(tmp_path / "image2.png", (0, 255, 0))
	img3 = _create_image(tmp_path / "image3.png", (0, 0, 255))
	output = tmp_path / "images_to_pdf.pdf"

	result = images_to_pdf([str(img1), str(img2), str(img3)], str(output))

	assert result == output
	with pikepdf.Pdf.open(result) as pdf:
		assert len(pdf.pages) == 3


def test_convert_jpg_images_to_pdf(tmp_path: Path) -> None:
	img1 = _create_image(tmp_path / "image4.jpg", (255, 255, 0))
	img2 = _create_image(tmp_path / "image5.jpg", (150, 0, 150))
	output = tmp_path / "jpg_images_to_pdf.pdf"

	result = images_to_pdf([str(img1), str(img2)], str(output))

	assert result == output
	with pikepdf.Pdf.open(result) as pdf:
		assert len(pdf.pages) == 2
