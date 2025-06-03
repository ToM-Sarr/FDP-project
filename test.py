import sys
import re
import fitz  # PyMuPDF
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel,
    QFileDialog, QTextEdit, QScrollArea
)
from PySide6.QtGui import QFont
from datetime import datetime


def clean_amount(amount_str):
    """Nettoie et convertit une chaîne de montant en float"""
    if not amount_str:
        return 0.0
    # Remplace les virgules par des points et supprime les espaces
    cleaned = amount_str.replace(",", ".").replace(" ", "")
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def extract_info(text):
    """Extrait toutes les informations pertinentes de la fiche de paie"""
    info = {}
    
    # === INFORMATIONS PERSONNELLES ===
    # Nom et prénom
    match = re.search(r"M\.\s+([A-Z]+)\s+([A-Za-z]+)", text)
    if match:
        info["Nom"] = match.group(1).title()
        info["Prénom"] = match.group(2).title()
    
    # Numéro de sécurité sociale
    match = re.search(r"N°\s*Sécurité\s*S\.\s*(\d+\s+\d+)", text)
    if match:
        info["Numéro Sécurité Sociale"] = match.group(1).replace(" ", "")
    
    # Adresse
    match = re.search(r"(\d+.*?)\s+(\d{5})\s+([A-Z\s]+)", text)
    if match:
        info["Adresse"] = f"{match.group(1)}, {match.group(2)} {match.group(3).strip()}"
    
    # === INFORMATIONS EMPLOYEUR ===
    # Entreprise
    match = re.search(r"(EXPLEO FRANCE TOULOUSE)", text)
    if match:
        info["Entreprise"] = match.group(1)
    
    # SIRET
    match = re.search(r"(\d{14})", text)
    if match:
        info["SIRET"] = match.group(1)
    
    # === INFORMATIONS CONTRAT ===
    # Poste
    match = re.search(r"(INGENIEUR|TECHNICIEN|CADRE)", text)
    if match:
        info["Poste"] = match.group(1)
    
    # Date d'entrée
    match = re.search(r"Date d'entrée\s+(\d{2}-\d{2}-\d{4})", text)
    if match:
        info["Date d'entrée"] = match.group(1)
    
    # Coefficient
    match = re.search(r"Coefficient\s+(\d+)", text)
    if match:
        info["Coefficient"] = int(match.group(1))
    
    # === PÉRIODE DE PAIE ===
    # Période du bulletin
    match = re.search(r"Période du\s+(\d{2}-\d{2}-\d{4})\s+au\s+(\d{2}-\d{2}-\d{4})", text)
    if match:
        info["Début Période"] = match.group(1)
        info["Fin Période"] = match.group(2)
    
    # Période de référence (pour les congés)
    match = re.search(r"Période de Référence\s+(\d{2}-\d{2}-\d{2})\s+au\s+(\d{2}-\d{2}-\d{2})", text)
    if match:
        info["Début Période Référence"] = match.group(1)
        info["Fin Période Référence"] = match.group(2)
    
    # === SALAIRES ET MONTANTS ===
    # Salaire de base
    match = re.search(r"Salaire de base\s+[\d,]+\s+[\d,]+\s+([\d\s,]+)", text)
    if match:
        info["Salaire de Base"] = clean_amount(match.group(1))
    
    # Brut fiscal
    match = re.search(r"BRUT\s+([\d\s,]+)", text)
    if match:
        info["Salaire Brut"] = clean_amount(match.group(1))
    
    # Brut fiscal (cumul)
    match = re.search(r"FISCAL\s+[\d\s,]+\s+([\d\s,]+)", text)
    if match:
        info["Brut Fiscal Cumul"] = clean_amount(match.group(1))
    
    # Net imposable
    match = re.search(r"Net Imposable\s+([\d\s,]+)", text)
    if match:
        info["Net Imposable"] = clean_amount(match.group(1))
    
    # Net social
    match = re.search(r"Net Social\s+([\d\s,]+)", text)
    if match:
        info["Net Social"] = clean_amount(match.group(1))
    
    # Net à payer avant impôt
    match = re.search(r"Net à payer avant impôt sur le revenu\s+([\d\s,]+)", text)
    if match:
        info["Net avant Impôt"] = clean_amount(match.group(1))
    
    # Net à payer final
    match = re.search(r"NET A PAYER\s+([\d\s,]+)\s*EUR", text)
    if match:
        info["Net à Payer"] = clean_amount(match.group(1))
    
    # === CHARGES ET COTISATIONS ===
    # Charges salariales totales
    match = re.search(r"Charges Salariales\s*-\s*([\d\s,]+)", text)
    if match:
        info["Charges Salariales"] = clean_amount(match.group(1))
    
    # Charges patronales totales
    match = re.search(r"Charges Patronales\s*-\s*([\d\s,]+)", text)
    if match:
        info["Charges Patronales"] = clean_amount(match.group(1))
    
    # Charges totales
    match = re.search(r"Charges Totales\s*-\s*([\d\s,]+)", text)
    if match:
        info["Charges Totales"] = clean_amount(match.group(1))
    
    # Total versé par l'employeur
    match = re.search(r"Total versé par l'employeur\s+([\d\s,]+)", text)
    if match:
        info["Total Employeur"] = clean_amount(match.group(1))
    
    # === COTISATIONS DÉTAILLÉES ===
    # Sécurité sociale
    match = re.search(r"SS Maladie.*?-(\d+,\d+)", text)
    if match:
        info["SS Maladie"] = clean_amount(match.group(1))
    
    # Complémentaire santé
    match = re.search(r"Complémentaire Santé.*?-(\d+,\d+)\s+-(\d+,\d+)", text)
    if match:
        info["Complémentaire Santé Salarié"] = clean_amount(match.group(1))
        info["Complémentaire Santé Employeur"] = clean_amount(match.group(2))
    
    # Retraite
    match = re.search(r"Retraite\s+([\d\s,]+)", text)
    if match:
        info["Plafond Retraite"] = clean_amount(match.group(1))
    
    # APEC
    match = re.search(r"APEC.*?-(\d+,\d+)\s+-(\d+,\d+)", text)
    if match:
        info["APEC Salarié"] = clean_amount(match.group(1))
        info["APEC Employeur"] = clean_amount(match.group(2))
    
    # CSG déductible
    match = re.search(r"CSG déductible.*?-(\d+,\d+)", text)
    if match:
        info["CSG Déductible"] = clean_amount(match.group(1))
    
    # CSG/RDS non déductible
    match = re.search(r"CSG/RDS non déduct.*?-(\d+,\d+)", text)
    if match:
        info["CSG Non Déductible"] = clean_amount(match.group(1))
    
    # === IMPÔTS ===
    # Impôt sur le revenu
    match = re.search(r"Impôt sur le revenu prélevé.*?([\d,]+)", text)
    if match:
        info["Impôt Prélevé"] = clean_amount(match.group(1))
    
    # Montant net imposable pour l'impôt
    match = re.search(r"Montant net imposable\s+([\d\s,]+)", text)
    if match:
        info["Base Impôt"] = clean_amount(match.group(1))
    
    # === CONGÉS ET RTT ===
    # Solde congés payés
    matches = re.findall(r"Solde CP\d+\s+([\d,]+)", text)
    if matches:
        total_cp = sum(clean_amount(match) for match in matches)
        info["Solde Congés Payés"] = total_cp
    
    # RTT salarié
    match = re.search(r"Solde RTT Salarié.*?(\d+,\d+)", text)
    if match:
        info["Solde RTT Salarié"] = clean_amount(match.group(1))
    
    # RTT employeur
    match = re.search(r"Solde RTT Empl.*?(\d+,\d+)", text)
    if match:
        info["Solde RTT Employeur"] = clean_amount(match.group(1))
    
    # === AVANTAGES ===
    # Indemnité télétravail
    match = re.search(r"Indemnité télétravail\s+([\d,]+)", text)
    if match:
        info["Indemnité Télétravail"] = clean_amount(match.group(1))
    
    # Titres restaurant
    match = re.search(r"Titres restaurant\s+-(\d+,\d+).*?-(\d+,\d+)", text)
    if match:
        info["Titres Restaurant"] = clean_amount(match.group(2))
    
    # === HEURES ===
    # Heures travaillées dans le mois
    hours_pattern = r"(\d+,\d+)\s+\d+,\d+\s+[\d\s,]+"
    match = re.search(r"Salaire de base\s+" + hours_pattern, text)
    if match:
        info["Heures Travaillées"] = clean_amount(match.group(1))
    
    # === INFORMATIONS BANCAIRES ===
    # IBAN
    match = re.search(r"IBAN([A-Z0-9\s]+)BIC", text)
    if match:
        info["IBAN"] = match.group(1).strip()
    
    # Date de virement
    match = re.search(r"(\d{2}-\d{2}-\d{4})", text)
    if match:
        info["Date Virement"] = match.group(1)
    
    return info


class PaieExtractor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Extracteur de Fiche de Paie - Version Complète")
        self.setMinimumSize(800, 600)

        layout = QVBoxLayout()

        # En-tête
        header = QLabel("📊 Extracteur Complet de Fiche de Paie")
        header.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(header)

        self.label = QLabel("Aucune fiche chargée - Chargez un PDF pour analyser toutes les données")
        self.label.setFont(QFont("Arial", 10))
        layout.addWidget(self.label)

        # Bouton de chargement
        self.button = QPushButton("📄 Charger une fiche de paie (PDF)")
        self.button.setFont(QFont("Arial", 12))
        self.button.clicked.connect(self.load_pdf)
        layout.addWidget(self.button)

        # Zone de résultats avec scroll
        scroll_area = QScrollArea()
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setFont(QFont("Courier", 10))
        scroll_area.setWidget(self.result_text)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)

        # Bouton d'export (optionnel pour plus tard)
        self.export_button = QPushButton("💾 Exporter les données (JSON)")
        self.export_button.clicked.connect(self.export_data)
        self.export_button.setEnabled(False)
        layout.addWidget(self.export_button)

        self.setLayout(layout)
        self.current_data = {}

    def load_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Choisir un fichier PDF", "", "Fichiers PDF (*.pdf)"
        )
        if file_path:
            self.label.setText(f"Fichier chargé : {file_path.split('/')[-1]}")
            text = self.extract_text_from_pdf(file_path)
            
            # Debug: afficher le texte extrait (commenté pour la production)
            # print("Texte extrait:", text[:500])
            
            infos = extract_info(text)
            self.current_data = infos

            if infos:
                output = self.format_output(infos)
                self.export_button.setEnabled(True)
            else:
                output = "❌ Aucune information trouvée. Vérifiez le format du PDF."
                self.export_button.setEnabled(False)

            self.result_text.setText(output)

    def format_output(self, infos):
        """Formate les informations extraites de manière organisée"""
        sections = {
            "👤 INFORMATIONS PERSONNELLES": [
                "Nom", "Prénom", "Numéro Sécurité Sociale", "Adresse"
            ],
            "🏢 INFORMATIONS EMPLOYEUR": [
                "Entreprise", "SIRET", "Poste", "Date d'entrée", "Coefficient"
            ],
            "📅 PÉRIODE": [
                "Début Période", "Fin Période", "Début Période Référence", "Fin Période Référence"
            ],
            "💰 SALAIRES": [
                "Salaire de Base", "Salaire Brut", "Brut Fiscal Cumul", "Net Imposable", 
                "Net Social", "Net avant Impôt", "Net à Payer"
            ],
            "📊 CHARGES": [
                "Charges Salariales", "Charges Patronales", "Charges Totales", "Total Employeur"
            ],
            "🏥 COTISATIONS SANTÉ": [
                "SS Maladie", "Complémentaire Santé Salarié", "Complémentaire Santé Employeur"
            ],
            "🏛️ COTISATIONS DIVERSES": [
                "Plafond Retraite", "APEC Salarié", "APEC Employeur", 
                "CSG Déductible", "CSG Non Déductible"
            ],
            "💸 IMPÔTS": [
                "Impôt Prélevé", "Base Impôt"
            ],
            "🏖️ CONGÉS & RTT": [
                "Solde Congés Payés", "Solde RTT Salarié", "Solde RTT Employeur"
            ],
            "🎁 AVANTAGES": [
                "Indemnité Télétravail", "Titres Restaurant"
            ],
            "⏰ TEMPS DE TRAVAIL": [
                "Heures Travaillées"
            ],
            "🏦 INFORMATIONS BANCAIRES": [
                "IBAN", "Date Virement"
            ]
        }
        
        output = []
        output.append("=" * 60)
        output.append("📋 ANALYSE COMPLÈTE DE LA FICHE DE PAIE")
        output.append("=" * 60)
        output.append("")
        
        for section_name, fields in sections.items():
            section_data = []
            for field in fields:
                if field in infos:
                    value = infos[field]
                    if isinstance(value, float):
                        if field in ["Heures Travaillées"]:
                            section_data.append(f"  {field:<25} : {value:.2f} h")
                        else:
                            section_data.append(f"  {field:<25} : {value:.2f} €")
                    else:
                        section_data.append(f"  {field:<25} : {value}")
            
            if section_data:
                output.append(f"{section_name}")
                output.append("-" * 40)
                output.extend(section_data)
                output.append("")
        
        # Résumé rapide
        if "Net à Payer" in infos and "Salaire Brut" in infos:
            taux_prelevement = ((infos["Salaire Brut"] - infos["Net à Payer"]) / infos["Salaire Brut"]) * 100
            output.append("📈 RÉSUMÉ")
            output.append("-" * 40)
            output.append(f"  Salaire Brut          : {infos['Salaire Brut']:.2f} €")
            output.append(f"  Net à Payer           : {infos['Net à Payer']:.2f} €")
            output.append(f"  Taux de prélèvement   : {taux_prelevement:.1f}%")
            output.append("")
        
        output.append("=" * 60)
        output.append(f"✅ Extraction terminée - {len(infos)} champs trouvés")
        output.append("=" * 60)
        
        return "\n".join(output)

    def export_data(self):
        """Exporte les données au format JSON"""
        if not self.current_data:
            return
        
        import json
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Exporter les données", "fiche_paie_data.json", "Fichiers JSON (*.json)"
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.current_data, f, indent=2, ensure_ascii=False)
                self.label.setText(f"Données exportées vers : {file_path.split('/')[-1]}")
            except Exception as e:
                self.label.setText(f"Erreur lors de l'export : {str(e)}")

    def extract_text_from_pdf(self, path):
        """Extrait le texte du PDF"""
        try:
            doc = fitz.open(path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        except Exception as e:
            return f"Erreur lors de la lecture du PDF : {str(e)}"


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PaieExtractor()
    window.show()
    sys.exit(app.exec())