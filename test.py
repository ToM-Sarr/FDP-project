import sys
import re
import fitz  # PyMuPDF
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel,
    QFileDialog, QTextEdit
)
from PySide6.QtGui import QFont


def extract_info(text):
    info = {}

    match = re.search(r"M\.\s+([A-Z]+)\s+([A-Za-z]+)", text)
    if match:
        info["Nom"] = match.group(1).title()
        info["Prénom"] = match.group(2).title()

    match = re.search(r"Salaire de base\s+\d+,\d+\s+\d+,\d+\s+([\d,.]+)", text)
    if match:
        info["Salaire Brut"] = float(match.group(1).replace(",", "."))

    match = re.search(r"NET A PAYER\s+([\d,.]+)EUR", text)
    if match:
        info["Net à Payer"] = float(match.group(1).replace(",", "."))

    match = re.search(r"Période de Référence\s+(\d{2}-\d{2}-\d{2}) au (\d{2}-\d{2}-\d{2})", text)
    if match:
        info["Début Période"] = match.group(1)
        info["Fin Période"] = match.group(2)

    match = re.search(r"Impôt sur le revenu prélevé.*?([\d,.]+)", text)
    if match:
        info["Impôt prélevé"] = float(match.group(1).replace(",", "."))

    return info


class PaieExtractor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Extracteur de Fiche de Paie")
        self.setMinimumSize(500, 400)

        layout = QVBoxLayout()

        self.label = QLabel("Aucune fiche chargée")
        self.label.setFont(QFont("Arial", 12))
        layout.addWidget(self.label)

        self.button = QPushButton("📄 Charger une fiche de paie (PDF)")
        self.button.clicked.connect(self.load_pdf)
        layout.addWidget(self.button)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        layout.addWidget(self.result_text)

        self.setLayout(layout)

    def load_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Choisir un fichier PDF", "", "Fichiers PDF (*.pdf)")
        if file_path:
            self.label.setText(f"Fichier chargé : {file_path.split('/')[-1]}")
            text = self.extract_text_from_pdf(file_path)
            infos = extract_info(text)

            if infos:
                output = "\n".join(f"{k} : {v}" for k, v in infos.items())
            else:
                output = "Aucune information trouvée."

            self.result_text.setText(output)

    def extract_text_from_pdf(self, path):
        doc = fitz.open(path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PaieExtractor()
    window.show()
    sys.exit(app.exec())
