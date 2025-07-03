from PyQt5.QtWidgets import (
    QFrame, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QSizePolicy
)
from PyQt5.QtCore import pyqtSignal

class ModuleCard(QFrame):
    runRequested = pyqtSignal(str)

    def __init__(self, title: str, filename: str, description: str = ""):
        super().__init__()
        self.filename = filename
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background-color: #2b2b2b;
                border-radius: 8px;
                padding: 12px;
            }
            QLabel#title {
                font-size: 16px;
                color: #ffffff;
            }
            QLabel#desc {
                font-size: 12px;
                color: #cccccc;
            }
            QPushButton {
                background-color: #0078d7;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
        """)

        title_label = QLabel(f"🧩 {title}")
        title_label.setObjectName("title")
        title_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        desc_label = QLabel(description)
        desc_label.setObjectName("desc")
        desc_label.setWordWrap(True)

        run_btn = QPushButton("Çalıştır")
        run_btn.clicked.connect(self.on_run_clicked)

        settings_btn = QPushButton("Ayarlar")
        settings_btn.clicked.connect(self.on_settings_clicked)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(run_btn)
        btn_layout.addWidget(settings_btn)
        btn_layout.addStretch()

        main_layout = QVBoxLayout()
        main_layout.addWidget(title_label)
        if description:
            main_layout.addWidget(desc_label)
        main_layout.addLayout(btn_layout)
        self.setLayout(main_layout)

    def on_run_clicked(self):
        self.runRequested.emit(self.filename)

    def on_settings_clicked(self):
        print(f"🔧 Ayarlar açılacak: {self.filename}")