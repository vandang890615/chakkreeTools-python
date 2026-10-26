"""
PySide6 Native Rebar Standards & Details Viewer Dialog
Shows standard hooks, lap splices, and minimum concrete cover specifications.
"""

from typing import Any, Optional
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QGroupBox,
    QLabel,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
)

from chakkree_tools.i18n import tr


class RebarToolsDialog(QDialog):
    """
    Informational and interactive reference dialog for Rebar standards.
    """

    def __init__(self, parent: Optional[Any] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(tr("Chakkree Rebar Tools & Standards (ว.ส.ท. / EIT)"))
        self.resize(520, 440)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)

        tabs = QTabWidget(self)

        # Tab 1: Standard Hooks
        tab1 = QTableWidget(4, 3, self)
        tab1.setHorizontalHeaderLabels([tr("Hook Type"), tr("Formula (db)"), tr("Minimum Extension")])
        hooks = [
            (tr("90° Standard Hook"), "12 x db", "6.5 cm"),
            (tr("180° Standard Hook"), "4 x db", "6.5 cm"),
            (tr("135° Stirrup Hook (Seismic)"), "6 x db", "7.5 cm"),
            (tr("90° Stirrup Hook"), "6 x db", "6.5 cm"),
        ]
        for row, (h_type, formula, min_ext) in enumerate(hooks):
            tab1.setItem(row, 0, QTableWidgetItem(h_type))
            tab1.setItem(row, 1, QTableWidgetItem(formula))
            tab1.setItem(row, 2, QTableWidgetItem(min_ext))
        tabs.addTab(tab1, tr("Standard Hooks"))

        # Tab 2: Concrete Cover
        tab2 = QTableWidget(4, 3, self)
        tab2.setHorizontalHeaderLabels([tr("Structural Member"), tr("Minimum Cover"), tr("Exposed to Earth/Weather")])
        covers = [
            (tr("Footing / Foundation"), "7.5 cm", "7.5 cm"),
            (tr("RC Column"), "4.0 cm", "4.0 cm"),
            (tr("RC Beam"), "4.0 cm", "4.0 cm"),
            (tr("RC Slab"), "2.0 cm", "2.5 cm"),
        ]
        for row, (member, cov, exp) in enumerate(covers):
            tab2.setItem(row, 0, QTableWidgetItem(member))
            tab2.setItem(row, 1, QTableWidgetItem(cov))
            tab2.setItem(row, 2, QTableWidgetItem(exp))
        tabs.addTab(tab2, tr("Concrete Cover"))

        # Tab 3: Lap Splice
        tab3 = QTableWidget(6, 3, self)
        tab3.setHorizontalHeaderLabels([tr("Rebar Size"), tr("Class B Tension Lap"), tr("Compression Lap")])
        splices = [
            ("DB12", "55 cm", "40 cm"),
            ("DB16", "75 cm", "50 cm"),
            ("DB20", "95 cm", "65 cm"),
            ("DB25", "120 cm", "80 cm"),
            ("DB28", "135 cm", "90 cm"),
            ("DB32", "155 cm", "105 cm"),
        ]
        for row, (sz, ten, comp) in enumerate(splices):
            tab3.setItem(row, 0, QTableWidgetItem(sz))
            tab3.setItem(row, 1, QTableWidgetItem(ten))
            tab3.setItem(row, 2, QTableWidgetItem(comp))
        tabs.addTab(tab3, tr("Lap Splices"))

        layout.addWidget(tabs)

        btn_box = QDialogButtonBox(QDialogButtonBox.Close, Qt.Horizontal, self)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)
