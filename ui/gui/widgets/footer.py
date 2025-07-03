from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout

class Footer(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout()
        layout.addStretch()
        layout.addWidget(QLabel("🔧 powered by Alitility"))
        self.setLayout(layout)