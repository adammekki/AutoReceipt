from fillpdf import fillpdfs
import json

test = rf"þÿ\u0000R\u0000ü\u0000c\u0000k"
print(test)  # Should print: þÿ\u0000R\u0000ü\u0000c\u0000k
print(repr(test))  # Should show single backslashes

print(json.dumps(fillpdfs.get_form_fields('/Users/adammekki/Desktop/Thesis/AutoReceipt/backend/app/example_reimbursement.pdf'), indent=4))
