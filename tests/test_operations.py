"""Unit tests for Phase 2 operation modules."""

from pathlib import Path

import pytest

pikepdf = pytest.importorskip("pikepdf")
fitz = pytest.importorskip("fitz")
PIL = pytest.importorskip("PIL.Image")

from kpdf.operations.image_converter import images_to_pdf
from kpdf.operations.pdf_compressor import compress_pdf
from kpdf.operations.pdf_extractor import extract_text_from_pdf
from kpdf.operations.pdf_merger import merge_pdfs
from kpdf.operations.pdf_rotator import rotate_pdf
from kpdf.operations.pdf_splitter import parse_page_ranges, split_pdf
from kpdf.utils.error_handler import OperationError


def _create_blank_pdf(path: Path, pages: int) -> Path:
    doc = pikepdf.Pdf.new()
    for _ in range(pages):
        doc.add_blank_page(page_size=(612, 792))
    doc.save(path)
    doc.close()
    return path


def _create_text_pdf(path: Path, text: str) -> Path:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), text)
    doc.save(path)
    doc.close()
    return path


def _create_image(path: Path) -> Path:
    image = PIL.new("RGB", (64, 64), color=(200, 30, 30))
    image.save(path)
    return path


def test_merge_pdfs(tmp_path: Path) -> None:
    first = _create_blank_pdf(tmp_path / "a.pdf", pages=1)
    second = _create_blank_pdf(tmp_path / "b.pdf", pages=2)
    output = tmp_path / "merged.pdf"

    result = merge_pdfs([str(first), str(second)], str(output))

    assert result == output
    with pikepdf.Pdf.open(output) as merged:
        assert len(merged.pages) == 3


def test_split_pdf_with_ranges(tmp_path: Path) -> None:
    source = _create_blank_pdf(tmp_path / "source.pdf", pages=5)
    output = tmp_path / "split.pdf"

    result = split_pdf(str(source), str(output), "1-2,5")

    assert result == output
    with pikepdf.Pdf.open(output) as split_result:
        assert len(split_result.pages) == 3


def test_parse_page_ranges_rejects_invalid() -> None:
    with pytest.raises(OperationError):
        parse_page_ranges("3-1", max_pages=5)


def test_rotate_pdf(tmp_path: Path) -> None:
    source = _create_blank_pdf(tmp_path / "source.pdf", pages=1)
    output = tmp_path / "rotated.pdf"

    result = rotate_pdf(str(source), str(output), 90)

    assert result == output
    with pikepdf.Pdf.open(output) as rotated:
        assert int(rotated.pages[0].get("/Rotate", 0)) == 90


def test_extract_text_and_write_output(tmp_path: Path) -> None:
    source = _create_text_pdf(tmp_path / "source_text.pdf", "Hello kPDF")
    output_txt = tmp_path / "out.txt"

    text = extract_text_from_pdf(str(source), str(output_txt))

    assert "Hello kPDF" in text
    assert output_txt.exists()
    assert "Hello kPDF" in output_txt.read_text(encoding="utf-8")


def test_images_to_pdf(tmp_path: Path) -> None:
    image_a = _create_image(tmp_path / "a.png")
    image_b = _create_image(tmp_path / "b.jpg")
    output = tmp_path / "images.pdf"

    result = images_to_pdf([str(image_a), str(image_b)], str(output))

    assert result == output
    with pikepdf.Pdf.open(output) as result_pdf:
        assert len(result_pdf.pages) == 2


def test_compress_pdf_creates_output(tmp_path: Path) -> None:
    source = _create_blank_pdf(tmp_path / "source.pdf", pages=3)
    output = tmp_path / "compressed.pdf"

    result = compress_pdf(str(source), str(output), profile="medium")

    assert result == output
    assert output.exists()
    with pikepdf.Pdf.open(output) as compressed:
        assert len(compressed.pages) == 3
