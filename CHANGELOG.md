# Changelog

## 1.0.0 - 2026-04-22

### Added
- Full desktop GUI for six PDF operations: merge, split, rotate, extract text, images to PDF, compress.
- Batch queue with background execution and cancellation.
- Drag-and-drop support for list inputs and single-file input fields.
- Reordering for merge/images input lists.
- File-type icons for supported input files.
- Improved operation completion summaries (page counts, character counts, compression ratio).
- Windows EXE packaging with embedded icon and version metadata.
- Inno Setup installer script: [build/kpdf-installer.iss](build/kpdf-installer.iss).
- CI and tag-based release workflows:
  - [.github/workflows/ci.yml](.github/workflows/ci.yml)
  - [.github/workflows/release-build.yml](.github/workflows/release-build.yml)

### Changed
- Version bumped to 1.0.0 in:
  - [src/kpdf/config.py](src/kpdf/config.py)
  - [pyproject.toml](pyproject.toml)
- Updated user and developer documentation in [README.md](README.md).
- Converted script-style tests into pytest tests for automatic collection.

### Fixed
- Extract Text crash caused by UI updates from a background worker thread.
- Status bar not refreshing correctly after operation completion.
- Icon loading issues in bundled EXE mode.
- Invalid file drop handling with clear user notifications.

### Test Status
- 24 tests collected.
- 24 tests passing.
