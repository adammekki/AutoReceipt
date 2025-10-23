import json
import os
from fillpdf import fillpdfs

os.remove("filled_form.pdf") if os.path.exists("filled_form.pdf") else None

pdf_dict = fillpdfs.get_form_fields("Dienstreiseantrag_11_12_2023_V2.pdf")

abrechnung_json = {
    "AntragstellerIn_Name_Vorname": pdf_dict.get("Name Vorname"),
    "E-Mail-dienstlich": pdf_dict.get("EMa Adresse"),
    "Telefon_dienstlich": pdf_dict.get("Telefon dienstlich"),
    "\u00fe\u00ff\u0000P\u0000r\u0000i\u0000v\u0000a\u0000t\u0000e\u0000_\u0000A\u0000n\u0000s\u0000c\u0000h\u0000r\u0000i\u0000f\u0000t\u0000_\u0000S\u0000t\u0000r\u0000a\u0000\u00df\u0000e\u0000_\u0000P\u0000L\u0000Z\u0000_\u0000W\u0000o\u0000h\u0000n\u0000o\u0000r\u0000t": pdf_dict.get("Wohnort"),
    "\u00fe\u00ff\u0000B\u0000e\u0000s\u0000c\u0000h\u0000\u00e4\u0000f\u0000t\u0000i\u0000g\u0000u\u0000n\u0000g\u0000s\u0000s\u0000t\u0000e\u0000l\u0000l\u0000e\u0000I\u0000n\u0000s\u0000t\u0000i\u0000t\u0000u\u0000t\u0000_\u0000e\u0000i\u0000n\u0000s\u0000c\u0000h\u0000l\u0000_\u0000A\u0000n\u0000s\u0000c\u0000h\u0000r\u0000i\u0000f\u0000t": pdf_dict.get("Institut"),
}

try:
    print("Filling PDF form with Antrag data...")
    fillpdfs.write_fillable_pdf("Reisekostenabrechnung_28_05_2024.pdf", "filled_form.pdf", abrechnung_json)
except Exception as e:
    print(f"Error filling PDF form: {e}")
finally:
    print("Process Complete")