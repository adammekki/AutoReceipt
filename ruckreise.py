import os
import google.generativeai as genai
from dotenv import load_dotenv
from PIL import Image
import io
import json
from pdf2image import convert_from_path
from fillpdf import fillpdfs

# Configuration and Setup (remains the same)
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables. Please set it in your .env file.")
genai.configure(api_key=GEMINI_API_KEY)

# Universal Document Preparation Function (handles PDF and image files)
def prepare_document_for_gemini(document_path):
    """
    Takes a path to an image (JPEG, PNG, etc.) or a PDF.
    If PDF, converts each page to a PIL Image.
    Returns a list of Gemini-compatible image parts.
    """
    gemini_image_parts = []

    if not os.path.exists(document_path):
        print(f"Error: Document not found at {document_path}. Skipping.")
        return []

    file_extension = os.path.splitext(document_path)[1].lower()

    if file_extension == '.pdf':
        print(f"Processing PDF: {document_path}")
        try:
            images_from_pdf = convert_from_path(document_path, poppler_path=os.getenv("POPPLER_PATH"))
            for i, img in enumerate(images_from_pdf):
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format='JPEG')
                gemini_image_parts.append({
                    'mime_type': 'image/jpeg',
                    'data': img_byte_arr.getvalue()
                })
            print(f"Converted PDF {document_path} into {len(images_from_pdf)} image page(s).")
        except Exception as e:
            print(f"Error converting PDF {document_path} to images: {e}")
            print("Ensure Poppler is installed and its 'bin' directory is in your system PATH.")
            return []
    elif file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']:
        print(f"Processing image: {document_path}")
        try:
            img = Image.open(document_path)
            img_byte_arr = io.BytesIO()
            image_format = img.format if img.format else 'JPEG'
            img.save(img_byte_arr, format=image_format)
            gemini_image_parts.append({
                'mime_type': f'image/{image_format.lower()}',
                'data': img_byte_arr.getvalue()
            })
        except Exception as e:
            print(f"Error loading image {document_path}: {e}. Skipping.")
    else:
        print(f"Unsupported file type: {document_path}. Only PDFs and common image formats are supported.")

    return gemini_image_parts

# Gemini API Call Function
def get_gemini_vision_response_multi_doc(document_paths_list, prompt):
    model = genai.GenerativeModel('gemini-2.5-flash')

    contents = [prompt]
    all_image_parts = []

    for doc_path in document_paths_list:
        prepared_parts = prepare_document_for_gemini(doc_path)
        all_image_parts.extend(prepared_parts)

    if not all_image_parts:
        print("No valid images could be prepared from the provided documents. Sending only prompt.")
        # If no images, still send prompt, but expect less relevant output if image-dependent
        if len(contents) == 1: # Only the prompt text
            return None # Or handle differently, e.g., send with a placeholder image if API allows
        
    contents.extend(all_image_parts) # Add all prepared image parts to the contents list

    try:
        response = model.generate_content(contents)
        return response.text
    except Exception as e:
        print(f"Error calling Gemini API with documents: {e}")
        return None

# Main Execution Block (using your test PDFs)
if __name__ == "__main__":
    all_document_paths = [
        "Receipt_Flight1.pdf",
        "Receipt_Flight2.pdf",
        "Receipt_Flight3.pdf",
        "Receipt_Parking.pdf"
    ]

    # Your Gemini prompt (as refined in previous steps)
    multi_doc_prompt = """
        You are an expert at extracting travel expense details from receipts. 
        You will be provided with one or more document images (converted from original images or PDF pages), 
        as well as the JSON output of the outbound journey (Hinreise). Using this information, 
        extract and infer details for the return journey (Rückreise).

        For each document, extract the following information and return it as a single JSON object within a list. 
        The JSON keys MUST exactly match the specified field names below. 
        If a field cannot be found or is not applicable, return its value as an empty string (""). 
        For amounts, extract the numerical value followed by the currency symbol. 

        If there are several documents, infer which belong to the return trip and merge them together into one consistent output.

        If a receipt represents both the outbound and return journeys (e.g., a roundtrip flight ticket covering both Hin- und Rückflug), 
        split the cost evenly between Hinreise and Rückreise (divide total by two). 
        If it only represents the outbound trip (Hinreise), ignore it. 
        If it only represents the return trip (Rückreise), extract it normally.

        You are also given the Hinreise JSON output to help identify overlapping information and prevent duplication.

        Output format:
        A JSON list containing exactly one JSON object with the following UTF-16 encoded keys:

        Required Fields for the receipt:
            - "þÿ\\u0000R\\u0000ü\\u0000c\\u0000k\\u0000r\\u0000e\\u0000i\\u0000s\\u0000e\\u0000 \\u0000v\\u0000o\\u0000n": "(Origin city/location of the return journey, e.g., 'Bangkok')"
            - "þÿ\\u0000R\\u0000ü\\u0000c\\u0000k\\u0000r\\u0000e\\u0000i\\u0000s\\u0000e\\u0000 \\u0000n\\u0000a\\u0000c\\u0000h": "(Destination city/location of the return journey, e.g., 'Blaustein-Arnegg')"
            - "þÿ\\u0000R\\u0000ü\\u0000c\\u0000k\\u0000r\\u0000e\\u0000i\\u0000s\\u0000e\\u0000 \\u0000a\\u0000m": "(Start date of the return journey, format: DD.MM.YYYY, e.g., '22.12.2024')"
            - "þÿ\\u0000R\\u0000ü\\u0000c\\u0000k\\u0000r\\u0000e\\u0000i\\u0000s\\u0000e\\u0000 \\u0000U\\u0000h\\u0000r\\u0000z\\u0000e\\u0000i\\u0000t": "(Start time of the return journey, format: HH:MM, e.g., '23:30')"
            - "þÿ\\u0000R\\u0000ü\\u0000c\\u0000k\\u0000r\\u0000e\\u0000i\\u0000s\\u0000e\\u0000 \\u0000E\\u0000n\\u0000d\\u0000e\\u0000 \\u0000a\\u0000m": "(End date of the return journey, format: DD.MM.YYYY, e.g., '23.12.2024')"
            - "þÿ\\u0000R\\u0000ü\\u0000c\\u0000k\\u0000r\\u0000e\\u0000i\\u0000s\\u0000e\\u0000 \\u0000E\\u0000n\\u0000d\\u0000e\\u0000 \\u0000U\\u0000h\\u0000r\\u0000z\\u0000e\\u0000i\\u0000t": "(End time of the return journey, format: HH:MM, e.g., '10:00')"
            - "Rückreise_Ort": "(Specific location of arrival, e.g., 'Wohnung', 'Dienststelle')"
            - "Verkehrsmittel Rückreise": "(Primary mode of transport, e.g., 'Flugzeug', 'Bahn', 'Eigenes_KfZ', 'Fahrgemeinschaft', 'Bus_Bahn_Strassenbahn', 'Schiff', 'Sonstiges')"
            - "Klasse Rückreise": "(Class of travel, choices are 'Klasse 1', 'Klasse 2'. Leave empty if not specified)"
            - "þÿ\\u0000F\\u0000u\\u0000l\\u0000u\\u0000g\\u0000z\\u0000e\\u0000u\\u0000g\\u0000_\\u0000R\\u0000ü\\u0000c\\u0000k\\u0000r\\u0000e\\u0000i\\u0000s\\u0000e": "(Cost for air travel on the return journey. If both Hin- and Rückflug on one receipt, divide by 2. Format: '717,31€')"
            - "þÿ\\u0000B\\u0000a\\u0000h\\u0000n\\u0000_\\u00001\\u0000u\\u00002\\u0000_\\u0000K\\u0000l\\u0000a\\u0000s\\u0000s\\u0000e\\u0000_\\u0000R\\u0000ü\\u0000c\\u0000k\\u0000r\\u0000e\\u0000i\\u0000s\\u0000e": "(Cost for train travel on the return journey, e.g., '44,00€' or '1. Klasse')"
            - "þÿ\\u0000E\\u0000i\\u0000g\\u0000e\\u0000n\\u0000e\\u0000s\\u0000_\\u0000K\\u0000f\\u0000Z\\u0000_\\u0000R\\u0000ü\\u0000c\\u0000k\\u0000r\\u0000e\\u0000i\\u0000s\\u0000e": "(Details for personal car usage, e.g., '174km')"
            - "þÿ\\u0000D\\u0000i\\u0000e\\u0000n\\u0000s\\u0000t\\u0000w\\u0000a\\u0000g\\u0000e\\u0000n\\u0000_\\u0000R\\u0000ü\\u0000c\\u0000k\\u0000r\\u0000e\\u0000i\\u0000s\\u0000e": "(Details for company car usage)"
            - "þÿ\\u0000F\\u0000a\\u0000h\\u0000r\\u0000g\\u0000e\\u0000m\\u0000e\\u0000i\\u0000n\\u0000s\\u0000c\\u0000h\\u0000a\\u0000f\\u0000t\\u0000_\\u0000R\\u0000ü\\u0000c\\u0000k\\u0000r\\u0000e\\u0000i\\u0000s\\u0000e": "(If part of a carpool for the return journey, e.g., 'Fahrgemeinschaft')"
            - "þÿ\\u0000S\\u0000o\\u0000n\\u0000s\\u0000t\\u0000i\\u0000g\\u0000e\\u0000s\\u0000_\\u0000R\\u0000ü\\u0000c\\u0000k\\u0000r\\u0000e\\u0000i\\u0000s\\u0000e": "(Any other relevant notes or costs for the return journey, e.g., 'Taxi 25€')"
            - "þÿ\\u0000B\\u0000u\\u0000s\\u0000_\\u0000B\\u0000a\\u0000h\\u0000n\\u0000_\\u0000S\\u0000t\\u0000r\\u0000a\\u0000ß\\u0000e\\u0000n\\u0000b\\u0000a\\u0000h\\u0000n\\u0000_\\u0000R\\u0000ü\\u0000c\\u0000k\\u0000r\\u0000e\\u0000i\\u0000s\\u0000e": "(Cost for local transport on the return journey, e.g., '15,00€ (Parken)')"
            - "þÿ\\u0000S\\u0000c\\u0000h\\u0000w\\u0000e\\u0000r\\u0000b\\u0000e\\u0000s\\u0000c\\u0000h\\u0000ä\\u0000d\\u0000i\\u0000g\\u0000t\\u0000_\\u0000R\\u0000ü\\u0000c\\u0000k\\u0000r\\u0000e\\u0000i\\u0000s\\u0000e": "(If the traveler is severely disabled for the return journey)"


            Hinreise Gemini API Response:
            {
                "Hinreise_von": "München", 
                "Hinreise_nach": "Bangkok",
                "Hinreise_Beginn": "12.12.2024",
                "Hinreise_Uhrzeit": "22:25",
                "Hinreise_Ort": "Wohnung",
                "Hinreise_Urlaubspot": null,
                "Verkehrsmittel Hinreise": "Flugzeug",
                "Klasse Hinreise": null,
                "Flugzeug_Hinreise": "667,31€",
                "Bahn_1u2_Klasse_Hinreise": "",
                "Eigenes_KfZ_Hinreise": "",
                "Dienstwagen_Hinreise": null,
                "Fahrgemeinschaft Hinreise": null,
                "Sonstiges_Hinreise": "Sitzplatzreservierung 45,00€, Parken 55,00€",
                "Bus_Bahn_Strassenbahn_Hinreise": "",
                "planmäßige_Abfahrt": null,
                "Schwerbeschädigt Hinreise": null
            }
    """

    print("\nSending requests to Gemini API for multiple documents (images and PDFs) in a single call...")
    gemini_response_text = get_gemini_vision_response_multi_doc(all_document_paths, multi_doc_prompt)

    if gemini_response_text:
        print("\nGemini API Response:")
        cleaned_response = gemini_response_text.strip('```json\n').strip('\n```')
        try:
            cleaned_response = json.loads(cleaned_response)
            print(json.dumps(cleaned_response[0], indent=2, ensure_ascii=False))
            print("\nFilling PDF form with extracted data...")
            os.remove("filled_form.pdf") if os.path.exists("filled_form.pdf") else None
            fillpdfs.write_fillable_pdf("Reisekostenabrechnung_28_05_2024.pdf", "filled_form.pdf", cleaned_response[0])
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON response: {e}")
            print("Raw Gemini Response:")
            print(gemini_response_text)
    else:
        print("\nFailed to get a response from Gemini API.")

    print("\nProcessing complete.")