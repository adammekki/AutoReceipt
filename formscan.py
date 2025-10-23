import json
from fillpdf import fillpdfs

pdf_dict = fillpdfs.get_form_fields("example_reimbursement.pdf")

print(json.dumps(pdf_dict, indent=4))

# test_json = {
# "\u00fe\u00ff\u0000p\u0000l\u0000a\u0000n\u0000m\u0000\u00e4\u0000\u00df\u0000i\u0000g\u0000e\u0000_\u0000A\u0000b\u0000f\u0000a\u0000h\u0000r\u0000t": "(If the outbound journey's departure was scheduled on time, otherwise null)",
# "\u00fe\u00ff\u0000S\u0000c\u0000h\u0000w\u0000e\u0000r\u0000b\u0000e\u0000s\u0000c\u0000h\u0000\u00e4\u0000d\u0000i\u0000g\u0000t\u0000 \u0000H\u0000i\u0000n\u0000r\u0000e\u0000i\u0000s\u0000e": "(If the traveler is severely disabled for the outbound journey, otherwise null)"

# }

# output_json = {}

# for key, value in test_json.items():
#     raw_bytes = key.encode('latin-1')
#     decoded = raw_bytes.decode('utf-16')
#     output_json[decoded] = value

# print(output_json)