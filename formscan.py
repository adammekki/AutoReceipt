import json
import fillpdf
from fillpdf import fillpdfs

pdf_dict = fillpdfs.get_form_fields("Reisekostenabrechnung_28_05_2024.pdf")

string = json.dumps(pdf_dict, indent=4)

raw_bytes = string.encode('latin-1')

decoded = raw_bytes.decode('utf-16-be')

print(json.dumps(decoded, indent=4))