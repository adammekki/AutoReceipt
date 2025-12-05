import json
import os
from fillpdf import fillpdfs


class antrag:
    def __init__(self, data_dir: str = "."):
        """
        Initialize antrag with a data directory for file operations.
        
        Args:
            data_dir: Directory where PDF files are located and output will be saved
        """
        self.data_dir = data_dir
    
    def main(self, supervisor_name: str = None):
        """
        Main execution method for antrag processing.
        
        Args:
            supervisor_name: Optional supervisor name override. If None, uses value from form.
        """
        uploads_dir = os.path.join(os.path.dirname(__file__), "uploads")
        dienstreise_path = os.path.join(uploads_dir, "Dienstreiseantrag.pdf")
        templates_dir = os.path.join(os.path.dirname(__file__), "templates")
        reisekosten_path = os.path.join(templates_dir, "Reisekostenabrechnung_28_05_2024.pdf")
        filled_form_path = os.path.join(templates_dir, "filled_form.pdf")

        
        # Remove existing filled form if it exists
        if os.path.exists(filled_form_path):
            os.remove(filled_form_path)

        pdf_dict = fillpdfs.get_form_fields(dienstreise_path)
        abrechnung_json = {
            "AntragstellerIn_Name_Vorname": pdf_dict.get("Name Vorname"),
            "E-Mail-dienstlich": pdf_dict.get("EMa Adresse"),
            "Telefon_dienstlich": pdf_dict.get("Telefon dienstlich"),
            "\u00fe\u00ff\u0000P\u0000r\u0000i\u0000v\u0000a\u0000t\u0000e\u0000_\u0000A\u0000n\u0000s\u0000c\u0000h\u0000r\u0000i\u0000f\u0000t\u0000_\u0000S\u0000t\u0000r\u0000a\u0000\u00df\u0000e\u0000_\u0000P\u0000L\u0000Z\u0000_\u0000W\u0000o\u0000h\u0000n\u0000o\u0000r\u0000t": pdf_dict.get("Wohnort"),
            "\u00fe\u00ff\u0000B\u0000e\u0000s\u0000c\u0000h\u0000\u00e4\u0000f\u0000t\u0000i\u0000g\u0000u\u0000n\u0000g\u0000s\u0000s\u0000t\u0000e\u0000l\u0000l\u0000e\u0000I\u0000n\u0000s\u0000t\u0000i\u0000t\u0000u\u0000t\u0000_\u0000e\u0000i\u0000n\u0000s\u0000c\u0000h\u0000l\u0000_\u0000A\u0000n\u0000s\u0000c\u0000h\u0000r\u0000i\u0000f\u0000t": pdf_dict.get("Institut"),
            "Kreditinstitut": pdf_dict.get("Kreditinstitut"),
            "BIC": pdf_dict.get("BIC"),
            "BAN": pdf_dict.get("IBAN"),
            "Tagegeld": "nein",
            "Drittmittelprojekt": "P" + pdf_dict.get("Kostenstelle"),
            "Genehmigung_der_Dienstreise_am__von": pdf_dict.get("Datum_6") + " ",
        }

        # If supervisor_name is provided, override it
        if supervisor_name:
            current_value = abrechnung_json.get('Genehmigung_der_Dienstreise_am__von', '')
            abrechnung_json['Genehmigung_der_Dienstreise_am__von'] = current_value[:11] + supervisor_name

        try:
            print("Filling PDF form with Antrag data...")
            fillpdfs.write_fillable_pdf(reisekosten_path, filled_form_path, abrechnung_json)
        except Exception as e:
            print(f"Error filling PDF form: {e}")
            raise
        finally:
            print("Antrag Process Complete")
