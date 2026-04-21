# Release Checklist - kPDF 1.0.0

## Pre-release
- [x] Version set to 1.0.0.
- [x] Changelog updated.
- [x] README updated for users and developers.
- [x] Full test suite passing (`python -m pytest tests -q`).
- [x] EXE build succeeds with embedded icon and version metadata.
- [x] Optional: code-sign EXE (self-signed local cert).

## Build
- [x] Build command:
  `conda run --no-capture-output -n kpdf pyinstaller build/kpdf.spec --distpath build/dist --workpath build/work --log-level INFO`
- [x] Output generated:
  [build/dist/kpdf.exe](build/dist/kpdf.exe)

## Installer
- [x] Inno Setup script created:
  [build/kpdf-installer.iss](build/kpdf-installer.iss)
- [x] Build installer (requires Inno Setup / `ISCC.exe` on machine).
- [x] Installer output generated:
  [build/installer/kPDF-1.0.0-Setup.exe](build/installer/kPDF-1.0.0-Setup.exe)
- [x] Optional: code-sign installer (self-signed local cert).

## Smoke Test
- [x] Launch EXE successfully.
- [ ] Run one happy-path action per core tab.
- [ ] Validate drag/drop, file reordering, and status summaries.

## Publish
- [x] Create git tag `v1.0.0`.
- [ ] Attach EXE (and installer if built) to release notes.
- [ ] Announce release.
