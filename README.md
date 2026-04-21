# kPDF

kPDF is a Windows desktop PDF utility built with Python and PySide6.

## Release

Current stable release: **1.0.0**

## Features

- Merge PDFs
- Split PDFs by ranges (for example `1-3,5,8-9`)
- Rotate pages (90, 180, 270)
- Extract text to preview and `.txt`
- Convert images to PDF (`jpg`, `jpeg`, `png`, `bmp`, `tif`, `tiff`)
- Compress PDFs (`low`, `medium`, `high` profiles)
- Batch queue with background execution
- Drag and drop inputs and reordering in list-based tabs

## Quick Start (Windows EXE)

1. Run `build/dist/kpdf.exe`.
2. Choose an operation tab.
3. Add or drag input files.
4. Confirm the auto-proposed output path (or override it).
5. Run the operation and monitor progress in `Batch Queue`.

## Developer Setup (Conda)

1. Create environment:

   `conda env create -f environment.yml`

2. Activate environment:

   `conda activate kpdf`

3. Run app:

   `python -m kpdf.main`

4. Run all tests:

   `python -m pytest tests -q`

## Build Release EXE

Run from repository root:

`pyinstaller build/kpdf.spec --distpath build/dist --workpath build/work --log-level INFO`

## Build Windows Installer (Inno Setup)

Installer script: `build/kpdf-installer.iss`

Example command (if Inno Setup is installed):

`"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" build\kpdf-installer.iss`

Installer output: `build/installer/kPDF-1.0.0-Setup.exe`

## Troubleshooting

- `Access is denied` when building EXE:
  Close all running `kpdf.exe` processes before rebuilding.
- No live output while building:
  Do not pipe the pyinstaller command to `Select-Object`; run it directly.
- Extracted text is empty:
  The source is likely scanned/image-only; OCR is not included in 1.0.0.
- High compression profile may increase size:
  `high` enables linearization, which can add overhead for tiny PDFs.

## Known Limitations

- No OCR for image-only/scanned PDFs.
- No Office-to-PDF conversion in 1.0.0.
- Windows-focused release path and installer.

## Release Notes (1.0.0)

- Completed all six core PDF operations with GUI integration.
- Added background batch processing with job monitoring.
- Added drag/drop support and file reordering in list-based tabs.
- Added tab/button UI polish and file-type icons.
- Added operation completion details (pages, chars, compression ratio).
- Packaged standalone Windows EXE with embedded app icon.
- Expanded automated tests and converted script checks to pytest.
