"""Create test PDF files for merge testing."""
from pathlib import Path
import pikepdf

# Create test directory
test_dir = Path("c:/Users/Klemen/Work/kpdf/test_pdfs")
test_dir.mkdir(exist_ok=True)

# Create first test PDF with 2 blank pages
pdf1 = pikepdf.Pdf.new()
pdf1.add_blank_page(page_size=(612, 792))
pdf1.add_blank_page(page_size=(612, 792))
pdf1_path = test_dir / "document1.pdf"
pdf1.save(pdf1_path)
pdf1.close()
print(f"Created: {pdf1_path} (2 pages)")

# Create second test PDF with 3 blank pages
pdf2 = pikepdf.Pdf.new()
pdf2.add_blank_page(page_size=(612, 792))
pdf2.add_blank_page(page_size=(612, 792))
pdf2.add_blank_page(page_size=(612, 792))
pdf2_path = test_dir / "document2.pdf"
pdf2.save(pdf2_path)
pdf2.close()
print(f"Created: {pdf2_path} (3 pages)")

# Create third test PDF with 1 page
pdf3 = pikepdf.Pdf.new()
pdf3.add_blank_page(page_size=(612, 792))
pdf3_path = test_dir / "document3.pdf"
pdf3.save(pdf3_path)
pdf3.close()
print(f"Created: {pdf3_path} (1 page)")

print("\nTest files ready for merge test")
print(f"Test directory: {test_dir}")
