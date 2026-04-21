"""Main window for the kPDF desktop app."""

from pathlib import Path
from typing import Callable

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QSizePolicy,
    QStatusBar,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

import sys
import pikepdf

from kpdf.config import APP_NAME, APP_VERSION
from kpdf.operations import (
    compress_pdf,
    extract_text_from_pdf,
    images_to_pdf,
    merge_pdfs,
    rotate_pdf,
    split_pdf,
)
from kpdf.operations.batch_processor import BatchProcessor, JobStatus
from kpdf.ui.job_monitor import JobMonitor
from kpdf.utils.error_handler import to_user_error


def _icon_for_file(path: str) -> QIcon:
    """Return a QIcon matching the file extension, or an empty icon."""
    ext = Path(path).suffix.lstrip(".").lower()
    # Resolve icons dir both in dev and PyInstaller bundle
    base = Path(sys._MEIPASS) if hasattr(sys, "_MEIPASS") else Path(__file__).parent.parent.parent.parent
    icon_path = base / "assets" / "icons" / f"{ext}.png"
    if icon_path.exists():
        return QIcon(str(icon_path))
    return QIcon()


def _add_file_item(list_widget: QListWidget, path: str) -> None:
    """Add a file path to a list widget with its file-type icon."""
    item = QListWidgetItem(_icon_for_file(path), path)
    list_widget.addItem(item)


class DroppableLineEdit(QLineEdit):
    """Single-file QLineEdit that accepts drag-and-drop of one file."""

    def __init__(self, accept_extensions=None, parent=None):
        super().__init__(parent)
        self.accept_extensions = accept_extensions or [".pdf"]
        self.setAcceptDrops(True)
        self.setPlaceholderText("Drop file here or use Browse…")

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls and any(urls[0].toLocalFile().lower().endswith(ext) for ext in self.accept_extensions):
                event.acceptProposedAction()
                return
        event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            path = event.mimeData().urls()[0].toLocalFile()
            if any(path.lower().endswith(ext) for ext in self.accept_extensions):
                self.setText(path)
                event.acceptProposedAction()
                return
            QMessageBox.warning(
                self.window(),
                "Invalid File",
                f"This field only accepts: {', '.join(self.accept_extensions)}",
            )
        event.ignore()


class DraggableListWidget(QListWidget):
    """List widget that supports drag-and-drop file addition and item reordering."""

    fileAdded = Signal(str)

    def __init__(self, parent=None, accept_extensions=None):
        super().__init__(parent)
        self.accept_extensions = accept_extensions or [".pdf", ".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"]
        self.setAcceptDrops(True)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setDragDropMode(QListWidget.DragDropMode.InternalMove)

    def dragEnterEvent(self, event):
        """Accept drag events with file paths."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event):
        """Accept drag move events."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)

    def dropEvent(self, event):
        """Handle dropped files."""
        if event.mimeData().hasUrls():
            rejected = []
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if any(file_path.lower().endswith(ext) for ext in self.accept_extensions):
                    _add_file_item(self, file_path)
                    self.fileAdded.emit(file_path)
                else:
                    rejected.append(Path(file_path).name)
            if rejected:
                QMessageBox.warning(
                    self.window(),
                    "Invalid File(s)",
                    "The following files were not added (wrong type):\n" + "\n".join(rejected),
                )
            event.acceptProposedAction()
        else:
            super().dropEvent(event)


class MainWindow(QMainWindow):
    """Top-level application window with feature tabs wired to backend operations."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} {APP_VERSION}")
        self.resize(980, 700)
        
        # Load and set application icon (works both in dev and bundled EXE)
        base = Path(sys._MEIPASS) if hasattr(sys, '_MEIPASS') else Path(__file__).parent.parent.parent.parent
        icon_path = base / "assets" / "kpdf_icon.png"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        
        self.batch_processor = BatchProcessor(max_workers=4)
        self.job_monitor = JobMonitor(self.batch_processor)
        self.job_counter = 0
        self._success_message_builders: dict[str, Callable[[str], str]] = {}
        
        # Enable drag and drop for the window
        self.setAcceptDrops(True)
        
        self._setup_ui()

    def _setup_ui(self) -> None:
        # Global stylesheet for vivid look
        self.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #c9d6e4;
                background: #ffffff;
                top: -1px;
            }
            QTabBar::tab {
                padding: 8px 18px;
                font-size: 13px;
                color: #2f4157;
                background: #e8edf3;
                border: 1px solid #c9d6e4;
                border-bottom: 1px solid #c9d6e4;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #ffffff;
                border-bottom: 1px solid #ffffff;
                color: #1d2d44;
            }
            QPushButton {
                padding: 7px 16px;
                font-size: 13px;
                border-radius: 4px;
                border: 1px solid #acc6e5;
                background-color: #eaf2fb;
                color: #1f3f60;
            }
            QPushButton:hover { background-color: #d8e9fb; }
            QPushButton[class="run"] {
                background-color: #2E86C1;
                color: white;
                font-weight: bold;
                padding: 9px 20px;
                border: 1px solid #2E86C1;
            }
            QPushButton[class="run"]:hover { background-color: #1A5276; }
            QStatusBar { font-size: 12px; }
            QStatusBar::item { border: none; }
        """)

        root = QWidget(self)
        layout = QVBoxLayout(root)

        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_merge_tab(),    "\U0001F4CB  Merge")
        self.tabs.addTab(self._build_split_tab(),    "\u2702\uFE0F  Split")
        self.tabs.addTab(self._build_rotate_tab(),   "\U0001F504  Rotate")
        self.tabs.addTab(self._build_extract_tab(),  "\U0001F4DD  Extract Text")
        self.tabs.addTab(self._build_images_tab(),   "\U0001F5BC\uFE0F  Images to PDF")
        self.tabs.addTab(self._build_compress_tab(), "\U0001F5DC\uFE0F  Compress")
        self.tabs.addTab(self._build_batch_tab(),    "\U0001F4E6  Batch Queue")

        status_bar = QStatusBar()
        status_bar.setSizeGripEnabled(False)
        self.status_label = QLabel("Ready")
        status_bar.addWidget(self.status_label)
        self.setStatusBar(status_bar)

        layout.addWidget(self.tabs)
        layout.setContentsMargins(8, 8, 8, 8)
        self.setCentralWidget(root)

        self.job_monitor.job_started.connect(self._on_job_started)
        self.job_monitor.job_completed.connect(self._on_job_completed)
        self.job_monitor.job_failed.connect(self._on_job_failed)
        self.job_monitor.job_cancelled.connect(self._on_job_cancelled)

    def dragEnterEvent(self, event):
        """Accept drag events with file paths on the main window."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        """Accept drag move events on the main window."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        """Handle dropped files on the main window - add to active tab's file list."""
        if event.mimeData().hasUrls():
            current_tab = self.tabs.currentIndex()
            files = [url.toLocalFile() for url in event.mimeData().urls()]
            rejected = []
            
            # Add files to appropriate list based on current tab
            if current_tab == 0:  # Merge tab
                for f in files:
                    if f.lower().endswith('.pdf'):
                        _add_file_item(self.merge_inputs, f)
                        if not self.merge_output.text().strip():
                            self.merge_output.setText(self._to_default_output(f, ".pdf", "merged"))
                    else:
                        rejected.append(Path(f).name)
            elif current_tab == 4:  # Images tab
                for f in files:
                    if any(f.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.bmp', '.tif', '.tiff']):
                        _add_file_item(self.images_inputs, f)
                        if not self.images_output.text().strip():
                            self.images_output.setText(self._to_default_output(f, ".pdf", "images"))
                    else:
                        rejected.append(Path(f).name)
            else:
                rejected = [Path(f).name for f in files]

            if rejected:
                QMessageBox.warning(
                    self,
                    "Invalid File(s)",
                    "The dropped file(s) are not valid for this tab:\n" + "\n".join(rejected),
                )
            
            event.acceptProposedAction()

    def _build_merge_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.merge_inputs = DraggableListWidget(accept_extensions=[".pdf"])
        add_btn = QPushButton("➕ Add PDFs")
        remove_btn = QPushButton("➖ Remove Selected")
        clear_btn = QPushButton("🧹 Clear")

        output_layout = QHBoxLayout()
        self.merge_output = QLineEdit()
        merge_output_browse = QPushButton("📁 Browse")
        output_layout.addWidget(self.merge_output)
        output_layout.addWidget(merge_output_browse)

        run_btn = QPushButton("\U0001F4CB  Merge PDFs")
        run_btn.setProperty("class", "run")

        button_row = QHBoxLayout()
        button_row.addWidget(add_btn)
        button_row.addWidget(remove_btn)
        button_row.addWidget(clear_btn)

        layout.addWidget(QLabel("Input PDFs"))
        layout.addWidget(self.merge_inputs)
        layout.addLayout(button_row)
        layout.addWidget(QLabel("Output PDF"))
        layout.addLayout(output_layout)
        layout.addWidget(run_btn)

        add_btn.clicked.connect(self._on_merge_add)
        remove_btn.clicked.connect(self._on_merge_remove)
        clear_btn.clicked.connect(self.merge_inputs.clear)
        self.merge_inputs.fileAdded.connect(self._on_merge_input_changed)
        merge_output_browse.clicked.connect(self._on_merge_output_browse)
        run_btn.clicked.connect(self._on_merge_run)

        return tab

    def _build_split_tab(self) -> QWidget:
        tab = QWidget()
        form = QFormLayout(tab)

        self.split_input = DroppableLineEdit(accept_extensions=[".pdf"])
        split_input_browse = QPushButton("📁 Browse")
        split_input_row = self._line_with_button(self.split_input, split_input_browse)

        self.split_output = DroppableLineEdit(accept_extensions=[".pdf"])
        split_output_browse = QPushButton("📁 Browse")
        split_output_row = self._line_with_button(self.split_output, split_output_browse)

        self.split_ranges = QLineEdit("1")
        run_btn = QPushButton("\u2702\uFE0F  Split PDF")
        run_btn.setProperty("class", "run")

        form.addRow("Input PDF", split_input_row)
        form.addRow("Output PDF", split_output_row)
        form.addRow("Page Ranges", self.split_ranges)
        form.addRow(run_btn)

        split_input_browse.clicked.connect(self._on_split_input_browse)
        split_output_browse.clicked.connect(self._on_split_output_browse)
        self.split_input.textChanged.connect(self._on_split_input_changed)
        run_btn.clicked.connect(self._on_split_run)

        return tab

    def _build_rotate_tab(self) -> QWidget:
        tab = QWidget()
        form = QFormLayout(tab)

        self.rotate_input = DroppableLineEdit(accept_extensions=[".pdf"])
        rotate_input_browse = QPushButton("📁 Browse")
        rotate_input_row = self._line_with_button(self.rotate_input, rotate_input_browse)

        self.rotate_output = DroppableLineEdit(accept_extensions=[".pdf"])
        rotate_output_browse = QPushButton("📁 Browse")
        rotate_output_row = self._line_with_button(self.rotate_output, rotate_output_browse)

        self.rotate_angle = QComboBox()
        self.rotate_angle.addItems(["90", "180", "270"])
        run_btn = QPushButton("\U0001F504  Rotate PDF")
        run_btn.setProperty("class", "run")

        form.addRow("Input PDF", rotate_input_row)
        form.addRow("Output PDF", rotate_output_row)
        form.addRow("Angle", self.rotate_angle)
        form.addRow(run_btn)

        rotate_input_browse.clicked.connect(self._on_rotate_input_browse)
        rotate_output_browse.clicked.connect(self._on_rotate_output_browse)
        self.rotate_input.textChanged.connect(self._on_rotate_input_changed)
        run_btn.clicked.connect(self._on_rotate_run)

        return tab

    def _build_extract_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)

        form = QFormLayout()
        self.extract_input = DroppableLineEdit(accept_extensions=[".pdf"])
        extract_input_browse = QPushButton("📁 Browse")
        extract_input_row = self._line_with_button(self.extract_input, extract_input_browse)

        self.extract_output = DroppableLineEdit(accept_extensions=[".txt"])
        extract_output_browse = QPushButton("📁 Browse")
        extract_output_row = self._line_with_button(self.extract_output, extract_output_browse)

        run_btn = QPushButton("\U0001F4DD  Extract Text")
        run_btn.setProperty("class", "run")
        self.extract_preview = QPlainTextEdit()
        self.extract_preview.setPlaceholderText("Extracted text preview appears here...")

        form.addRow("Input PDF", extract_input_row)
        form.addRow("Output .txt (optional)", extract_output_row)

        layout.addLayout(form)
        layout.addWidget(run_btn)
        layout.addWidget(QLabel("Preview"))
        layout.addWidget(self.extract_preview)

        extract_input_browse.clicked.connect(self._on_extract_input_browse)
        extract_output_browse.clicked.connect(self._on_extract_output_browse)
        self.extract_input.textChanged.connect(self._on_extract_input_changed)
        run_btn.clicked.connect(self._on_extract_run)

        return tab

    def _build_images_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.images_inputs = DraggableListWidget(
            accept_extensions=[".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"]
        )

        add_btn = QPushButton("➕ Add Images")
        remove_btn = QPushButton("➖ Remove Selected")
        clear_btn = QPushButton("🧹 Clear")

        output_layout = QHBoxLayout()
        self.images_output = QLineEdit()
        images_output_browse = QPushButton("📁 Browse")
        output_layout.addWidget(self.images_output)
        output_layout.addWidget(images_output_browse)

        run_btn = QPushButton("\U0001F5BC\uFE0F  Convert Images to PDF")
        run_btn.setProperty("class", "run")

        button_row = QHBoxLayout()
        button_row.addWidget(add_btn)
        button_row.addWidget(remove_btn)
        button_row.addWidget(clear_btn)

        layout.addWidget(QLabel("Input Images"))
        layout.addWidget(self.images_inputs)
        layout.addLayout(button_row)
        layout.addWidget(QLabel("Output PDF"))
        layout.addLayout(output_layout)
        layout.addWidget(run_btn)

        add_btn.clicked.connect(self._on_images_add)
        remove_btn.clicked.connect(self._on_images_remove)
        clear_btn.clicked.connect(self.images_inputs.clear)
        self.images_inputs.fileAdded.connect(self._on_images_input_changed)
        images_output_browse.clicked.connect(self._on_images_output_browse)
        run_btn.clicked.connect(self._on_images_run)

        return tab

    def _build_compress_tab(self) -> QWidget:
        tab = QWidget()
        form = QFormLayout(tab)

        self.compress_input = DroppableLineEdit(accept_extensions=[".pdf"])
        compress_input_browse = QPushButton("📁 Browse")
        compress_input_row = self._line_with_button(self.compress_input, compress_input_browse)

        self.compress_output = DroppableLineEdit(accept_extensions=[".pdf"])
        compress_output_browse = QPushButton("📁 Browse")
        compress_output_row = self._line_with_button(self.compress_output, compress_output_browse)

        self.compress_profile = QComboBox()
        self.compress_profile.addItems(["low", "medium", "high"])
        run_btn = QPushButton("\U0001F5DC\uFE0F  Compress PDF")
        run_btn.setProperty("class", "run")

        form.addRow("Input PDF", compress_input_row)
        form.addRow("Output PDF", compress_output_row)
        form.addRow("Profile", self.compress_profile)
        form.addRow(run_btn)

        compress_input_browse.clicked.connect(self._on_compress_input_browse)
        compress_output_browse.clicked.connect(self._on_compress_output_browse)
        self.compress_input.textChanged.connect(self._on_compress_input_changed)
        run_btn.clicked.connect(self._on_compress_run)

        return tab

    def _build_batch_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)

        layout.addWidget(QLabel("Job Queue"))
        self.batch_job_list = QListWidget()
        layout.addWidget(self.batch_job_list)

        button_row = QHBoxLayout()
        refresh_btn = QPushButton("Refresh")
        clear_completed_btn = QPushButton("Clear Completed")
        cancel_selected_btn = QPushButton("Cancel Selected")
        button_row.addWidget(refresh_btn)
        button_row.addWidget(clear_completed_btn)
        button_row.addWidget(cancel_selected_btn)
        layout.addLayout(button_row)

        refresh_btn.clicked.connect(self._on_batch_refresh)
        clear_completed_btn.clicked.connect(self._on_batch_clear_completed)
        cancel_selected_btn.clicked.connect(self._on_batch_cancel_selected)

        return tab

    @staticmethod
    def _line_with_button(line: QLineEdit, button: QPushButton) -> QWidget:
        container = QWidget()
        row = QHBoxLayout(container)
        row.setContentsMargins(0, 0, 0, 0)
        row.addWidget(line)
        row.addWidget(button)
        return container

    @staticmethod
    def _to_default_output(input_path: str, suffix: str, stem_suffix: str) -> str:
        source = Path(input_path)
        if not source.name:
            return ""
        return str(source.with_name(f"{source.stem}_{stem_suffix}{suffix}"))

    def _set_output_if_empty(self, output_line: QLineEdit, input_path: str, suffix: str, stem_suffix: str) -> None:
        if input_path and not output_line.text().strip():
            output_line.setText(self._to_default_output(input_path, suffix, stem_suffix))

    def _on_merge_input_changed(self, input_path: str) -> None:
        self._set_output_if_empty(self.merge_output, input_path, ".pdf", "merged")

    def _on_images_input_changed(self, input_path: str) -> None:
        self._set_output_if_empty(self.images_output, input_path, ".pdf", "images")

    def _on_split_input_changed(self, input_path: str) -> None:
        self._set_output_if_empty(self.split_output, input_path, ".pdf", "split")

    def _on_rotate_input_changed(self, input_path: str) -> None:
        self._set_output_if_empty(self.rotate_output, input_path, ".pdf", "rotated")

    def _on_extract_input_changed(self, input_path: str) -> None:
        self._set_output_if_empty(self.extract_output, input_path, ".txt", "text")

    def _on_compress_input_changed(self, input_path: str) -> None:
        self._set_output_if_empty(self.compress_output, input_path, ".pdf", "compressed")

    def _handle_success(self, message: str) -> None:
        self.status_label.setText(message)
        QMessageBox.information(self, "Success", message)

    def _handle_failure(self, exc: Exception) -> None:
        error = to_user_error(exc)
        self.status_label.setText(error.message)
        QMessageBox.critical(self, error.title, error.message)

    def _on_merge_add(self) -> None:
        files, _ = QFileDialog.getOpenFileNames(self, "Select PDF files", "", "PDF Files (*.pdf)")
        for path in files:
            _add_file_item(self.merge_inputs, path)
        if files and not self.merge_output.text().strip():
            self.merge_output.setText(self._to_default_output(files[0], ".pdf", "merged"))

    def _on_merge_remove(self) -> None:
        for item in self.merge_inputs.selectedItems():
            self.merge_inputs.takeItem(self.merge_inputs.row(item))

    def _on_merge_output_browse(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Select output PDF", "", "PDF Files (*.pdf)")
        if path:
            self.merge_output.setText(path)

    def _on_merge_run(self) -> None:
        try:
            inputs = [self.merge_inputs.item(idx).text() for idx in range(self.merge_inputs.count())]
            output = self.merge_output.text().strip()

            def merge_operation():
                return merge_pdfs(inputs, output)

            def merge_success_message(output_path: str) -> str:
                page_count = self._pdf_page_count(output_path)
                return f"Merged {len(inputs)} files into {page_count} pages."

            self._submit_batch_job("Merge PDFs", merge_operation, merge_success_message)
        except Exception as exc:
            self._handle_failure(exc)

    def _on_split_input_browse(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Select input PDF", "", "PDF Files (*.pdf)")
        if path:
            self.split_input.setText(path)
            if not self.split_output.text().strip():
                self.split_output.setText(self._to_default_output(path, ".pdf", "split"))

    def _on_split_output_browse(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Select output PDF", "", "PDF Files (*.pdf)")
        if path:
            self.split_output.setText(path)

    def _on_split_run(self) -> None:
        try:
            input_pdf = self.split_input.text().strip()
            output_pdf = self.split_output.text().strip()
            ranges = self.split_ranges.text().strip()

            def split_operation():
                return split_pdf(input_pdf, output_pdf, ranges)

            def split_success_message(output_path: str) -> str:
                page_count = self._pdf_page_count(output_path)
                return f"Split created {page_count} pages ({ranges})."

            self._submit_batch_job("Split PDF", split_operation, split_success_message)
        except Exception as exc:
            self._handle_failure(exc)

    def _on_rotate_input_browse(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Select input PDF", "", "PDF Files (*.pdf)")
        if path:
            self.rotate_input.setText(path)
            if not self.rotate_output.text().strip():
                self.rotate_output.setText(self._to_default_output(path, ".pdf", "rotated"))

    def _on_rotate_output_browse(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Select output PDF", "", "PDF Files (*.pdf)")
        if path:
            self.rotate_output.setText(path)

    def _on_rotate_run(self) -> None:
        try:
            input_pdf = self.rotate_input.text().strip()
            output_pdf = self.rotate_output.text().strip()
            angle = int(self.rotate_angle.currentText())

            def rotate_operation():
                return rotate_pdf(input_pdf, output_pdf, angle)

            def rotate_success_message(output_path: str) -> str:
                page_count = self._pdf_page_count(output_path)
                return f"Rotated {page_count} pages by {angle} degrees."

            self._submit_batch_job("Rotate PDF", rotate_operation, rotate_success_message)
        except Exception as exc:
            self._handle_failure(exc)

    def _on_extract_input_browse(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Select input PDF", "", "PDF Files (*.pdf)")
        if path:
            self.extract_input.setText(path)
            if not self.extract_output.text().strip():
                self.extract_output.setText(self._to_default_output(path, ".txt", "text"))

    def _on_extract_output_browse(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Select output text file", "", "Text Files (*.txt)")
        if path:
            self.extract_output.setText(path)

    def _on_extract_run(self) -> None:
        try:
            input_pdf = self.extract_input.text().strip()
            output_txt = self.extract_output.text().strip() or None

            def extract_operation():
                extract_text_from_pdf(input_pdf, output_txt)
                return Path(output_txt) if output_txt else Path(input_pdf).with_suffix('.txt')

            def extract_success_message(output_path: str) -> str:
                text_path = Path(output_path)
                extracted = text_path.read_text(encoding="utf-8") if text_path.exists() else ""
                self.extract_preview.setPlainText(extracted)
                return f"Extracted {len(extracted)} characters to {text_path.name}."

            self._submit_batch_job("Extract Text", extract_operation, extract_success_message)
        except Exception as exc:
            self._handle_failure(exc)

    def _on_images_add(self) -> None:
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select image files",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.tif *.tiff)",
        )
        for path in files:
            _add_file_item(self.images_inputs, path)
        if files and not self.images_output.text().strip():
            self.images_output.setText(self._to_default_output(files[0], ".pdf", "images"))

    def _on_images_remove(self) -> None:
        for item in self.images_inputs.selectedItems():
            self.images_inputs.takeItem(self.images_inputs.row(item))

    def _on_images_output_browse(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Select output PDF", "", "PDF Files (*.pdf)")
        if path:
            self.images_output.setText(path)

    def _on_images_run(self) -> None:
        try:
            inputs = [self.images_inputs.item(idx).text() for idx in range(self.images_inputs.count())]
            output = self.images_output.text().strip()

            def images_operation():
                return images_to_pdf(inputs, output)

            def images_success_message(output_path: str) -> str:
                page_count = self._pdf_page_count(output_path)
                return f"Converted {len(inputs)} images into {page_count} PDF pages."

            self._submit_batch_job("Images to PDF", images_operation, images_success_message)
        except Exception as exc:
            self._handle_failure(exc)

    def _on_compress_input_browse(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Select input PDF", "", "PDF Files (*.pdf)")
        if path:
            self.compress_input.setText(path)
            if not self.compress_output.text().strip():
                self.compress_output.setText(self._to_default_output(path, ".pdf", "compressed"))

    def _on_compress_output_browse(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Select output PDF", "", "PDF Files (*.pdf)")
        if path:
            self.compress_output.setText(path)

    def _on_compress_run(self) -> None:
        try:
            input_pdf = self.compress_input.text().strip()
            output_pdf = self.compress_output.text().strip()
            profile = self.compress_profile.currentText()
            source_size = Path(input_pdf).stat().st_size if Path(input_pdf).exists() else 0

            def compress_operation():
                return compress_pdf(input_pdf, output_pdf, profile)

            def compress_success_message(output_path: str) -> str:
                out_size = Path(output_path).stat().st_size if Path(output_path).exists() else 0
                if source_size > 0:
                    ratio = (out_size / source_size) * 100
                    change = ((out_size - source_size) / source_size) * 100
                    return (
                        f"Compression ({profile}): {source_size:,} -> {out_size:,} bytes "
                        f"({ratio:.1f}% of original, {change:+.1f}%)."
                    )
                return f"Compression ({profile}) completed: {out_size:,} bytes."

            self._submit_batch_job("Compress PDF", compress_operation, compress_success_message)
        except Exception as exc:
            self._handle_failure(exc)

    def _on_job_started(self, job_id: str, job_name: str) -> None:
        self.status_label.setText(f"Running: {job_name}")
        self._update_batch_list()

    def _on_job_completed(self, job_id: str, job_name: str, output_path: str) -> None:
        message_builder = self._success_message_builders.pop(job_id, None)
        details = ""
        if message_builder:
            try:
                details = message_builder(output_path)
            except Exception as exc:
                details = f"Job completed, but stats failed: {exc}"

        status_text = f"\u2705 Completed: {job_name}"
        if details:
            status_text = f"{status_text} - {details}"

        self.status_label.setText(status_text)
        self._update_batch_list()
        QTimer.singleShot(4000, lambda: self.status_label.setText("Ready"))
        success_message = f"Job completed: {job_name}"
        if details:
            success_message = f"{success_message}\n\n{details}"
        self._handle_success(success_message)

    def _on_job_failed(self, job_id: str, job_name: str, error_msg: str) -> None:
        self._success_message_builders.pop(job_id, None)
        self.status_label.setText(f"\u274C Failed: {job_name}")
        self._update_batch_list()
        QTimer.singleShot(6000, lambda: self.status_label.setText("Ready"))
        self._handle_failure(Exception(error_msg))

    def _on_job_cancelled(self, job_id: str, job_name: str) -> None:
        self._success_message_builders.pop(job_id, None)
        self.status_label.setText(f"\u23F9 Cancelled: {job_name}")
        self._update_batch_list()
        QTimer.singleShot(4000, lambda: self.status_label.setText("Ready"))

    def _update_batch_list(self) -> None:
        self.batch_job_list.clear()
        for job in self.batch_processor.list_jobs():
            status_str = job.status.value
            item_text = f"[{status_str.upper()}] {job.name}"
            self.batch_job_list.addItem(item_text)

    def _on_batch_refresh(self) -> None:
        self._update_batch_list()

    def _on_batch_clear_completed(self) -> None:
        completed_ids = [
            job.job_id for job in self.batch_processor.list_jobs()
            if job.status in (JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED)
        ]
        for job_id in completed_ids:
            del self.batch_processor.jobs[job_id]
        self._update_batch_list()

    def _on_batch_cancel_selected(self) -> None:
        for job in self.batch_processor.list_jobs():
            if job.status == JobStatus.PENDING or job.status == JobStatus.RUNNING:
                self.batch_processor.cancel_job(job.job_id)
        self._update_batch_list()

    @staticmethod
    def _pdf_page_count(path: str) -> int:
        with pikepdf.Pdf.open(path) as pdf:
            return len(pdf.pages)

    def _submit_batch_job(
        self,
        name: str,
        operation_fn,
        success_message_builder: Callable[[str], str] | None = None,
    ) -> None:
        """Submit an operation to the batch processor instead of running synchronously."""
        self.job_counter += 1
        job_id = f"job_{self.job_counter}"
        job = self.batch_processor.submit_job(job_id, name, operation_fn)
        if success_message_builder:
            self._success_message_builders[job_id] = success_message_builder
        self.job_monitor.watch_job(job_id)
        self._update_batch_list()
