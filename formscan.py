import json
from fillpdf import fillpdfs

scan = fillpdfs.get_form_fields("example_reimbursement.pdf")

print(json.dumps(scan, ensure_ascii=False, indent=2))