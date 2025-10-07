import json
import fillpdf
from fillpdf import fillpdfs

pdf_dict = fillpdfs.get_form_fields("Reisekostenabrechnung_28_05_2024.pdf")

# print(json.dumps(pdf_dict, indent=4))

data_dict = {
    "AntragstellerIn_Name_Vorname": "Adam Mekki",
    "Personalnummer": "9878246529",
    "E-Mail-dienstlich": "adam@example.com",
    "Telefon_dienstlich": "022998844"
}

fillpdfs.write_fillable_pdf("Reisekostenabrechnung_28_05_2024.pdf", "filled_form.pdf", data_dict)