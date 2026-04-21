# kPDF

I want to create a PDF utility for windows, that can do the following:

1. Merge multiple PDF files into one.
2. Split a PDF file into multiple files.
3. Extract text from a PDF file.
4. Convert images to PDF.
5. Compress PDF files to reduce their size.
6. Rotate PDF pages.
7. Convert other formats to PDF (e.g., Word, Excel, PowerPoint).
8. Support batch processing for all the above features.
9. Provide a user-friendly interface for easy navigation and operation.
10. Ensure compatibility with all versions of PDF files.

# Implementation Guidelines

Use Python for development, with a desktop GUI and Windows EXE packaging.

## Recommended Tech Stack

1. Language: Python
2. GUI: PySide6 (Qt for Python)
3. EXE Packaging: PyInstaller
4. PDF Core Operations (merge, split, rotate, compress): pikepdf
5. Text Extraction: PyMuPDF
6. Images to PDF: img2pdf + Pillow
7. Batch Processing: concurrent.futures (ThreadPoolExecutor)


## Build and Distribution Plan

1. Use conda environment to manage dependencies and ensure reproducibility.
2. Build the app locally with dependencies in the conda environment.
3. Package the app as a Windows EXE using PyInstaller.
4. End users run the EXE without needing Python installed.

Example build command:

```powershell
pyinstaller --onefile --noconsole --name kpdf app.py
```

## Suggested Delivery Order

1. Deliver core PDF tools first (merge, split, rotate, extract text, images to PDF, compress).
2. Add batch processing and polish the GUI.
3. Add Office conversion features after MVP due to higher complexity and quality risks.

