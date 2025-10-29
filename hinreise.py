import os
import google.generativeai as genai
from dotenv import load_dotenv
from PIL import Image
import io
import json
from pdf2image import convert_from_path
from fillpdf import fillpdfs

class hinreise:
    def __init__(self, response):
        self.response = response

    # Configuration and Setup (remains the same)
    load_dotenv()
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not found in environment variables. Please set it in your .env file.")
    genai.configure(api_key=GEMINI_API_KEY)

    # Universal Document Preparation Function (handles PDF and image files)
    @staticmethod
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
                # convert_from_path returns a list of PIL Image objects, one for each page
                # You can adjust dpi for higher quality if needed, e.g., dpi=300
                images_from_pdf = convert_from_path(document_path, poppler_path=os.getenv("POPPLER_PATH"))
                for i, img in enumerate(images_from_pdf):
                    img_byte_arr = io.BytesIO()
                    img.save(img_byte_arr, format='JPEG') # Convert to JPEG bytes for Gemini
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
    @staticmethod
    def get_gemini_vision_response_multi_doc(document_paths_list, prompt):
        model = genai.GenerativeModel('gemini-2.5-flash')

        contents = [prompt]
        all_image_parts = []

        for doc_path in document_paths_list:
            prepared_parts = hinreise.prepare_document_for_gemini(doc_path)
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
    def main(self):
        all_document_paths = [
            "Receipt_Flight1.pdf",
            "Receipt_Flight2.pdf",
            "Receipt_Flight3.pdf",
            "Receipt_Parking.pdf"
        ]

        # Your Gemini prompt (as refined in previous steps)
        multi_doc_prompt = """
        You are an expert at extracting travel expense details from receipts. You will be provided with one or more document images (converted from original images or PDF pages). For each document, extract the following information and return it as a JSON object within a list. The JSON keys MUST exactly match the specified field names below. If a field cannot be found or is not applicable for a specific receipt, return its value as null for that receipt. For amounts, extract the numerical value followed by the currency symbol. If there are several documents, infer the data that is likely to be connected and merge them together into one output. Instead of using None, use empty string.

        If a receipt represents both the outbound and return journeys (e.g., a roundtrip flight ticket covering both Hin- und Rückflug), **split the cost evenly** between Hinreise and Rückreise, dividing the total by two.

        If the receipt only covers the return trip (Rückreise to Germany), ignore it.

        Output format: A JSON list where each element is a JSON object representing one receipt's extracted data.

        Required Fields for the receipt:
        - Hinreise_von: (Origin city/location of the outbound journey, e.g., "Blaustein-Arnegg")
        - Hinreise_nach: (Destination city/location of the outbound journey, e.g., "Bangkok")
        - Hinreise_Beginn: (Start date of the outbound journey, format: DD.MM.YYYY, e.g., "12.12.2024")
        - Hinreise_Uhrzeit: (Start time of the outbound journey, format: HH:MM, e.g., "17:00")
        - Hinreise_Ort: (Specific location of departure, either 'Wohnung', 'Dienststelle')
        - Hinreise_Urlaubsort: (If the outbound journey ends at a vacation spot before the official trip, otherwise null)
        - Verkehrsmittel Hinreise: (Primary mode of transport for the outbound journey, e.g., "Flugzeug", "Bahn", "Eigenes_KfZ", "Fahrgemeinschaft", "Bus_Bahn_Strassenbahn", "Schiff", "Sonstiges")
        - Klasse Hinreise: (Class of travel if applicable, either 'Klasse 2', 'Klasse 1'. If not specified, null.)
        - Flugzeug_Hinreise: (Cost for air travel on the outbound journey. Extract numerical value followed by currency symbol, e.g., "1234,56€". This can not be left null)
        - Bahn_1u2_Klasse_Hinreise: (Cost for train travel on the outbound journey, including class details. Extract numerical value followed by currency symbol, e.g., "44,00€" or "1. Klasse")
        - Eigenes_KfZ_Hinreise: (Details for personal car usage on the outbound journey. Extract distance in km and any parking notes, e.g., "88km Parken Freising")
        - Dienstwagen_Hinreise: (Details for company car usage on the outbound journey, if applicable. Otherwise null.)
        - Fahrgemeinschaft Hinreise: (If part of a carpool for the outbound journey, state "Fahrgemeinschaft". Otherwise null.)
        - Sonstiges_Hinreise: (Any other relevant notes or costs for the outbound journey not covered by specific transport fields, e.g., "(Hin- und Rückflug)", "Taxi 25€")
        - Bus_Bahn_Strassenbahn_Hinreise: (Cost for bus, tram, or local train travel on the outbound journey. Extract numerical value followed by currency symbol and any notes, e.g., "55,00€ (Parken)", do not put the flight cost here)
        - planmäßige_Abfahrt: "(If the outbound journey's departure was scheduled on time, otherwise null).
        - Schwerbeschädigt Hinreise: '(If the traveler is severely disabled for the outbound journey, otherwise null).
        """

        print("\nSending requests to Gemini API for multiple documents (images and PDFs) in a single call...")
        gemini_response_text = hinreise.get_gemini_vision_response_multi_doc(all_document_paths, multi_doc_prompt)

        if gemini_response_text:
            print("\nGemini API Response:")
            cleaned_response = gemini_response_text.strip('```json\n').strip('\n```')
            try:
                cleaned_response = json.loads(cleaned_response)
                print(json.dumps(cleaned_response[0], indent=2, ensure_ascii=False))
                print("\nFilling PDF form with extracted data...")
                fillpdfs.write_fillable_pdf("filled_form.pdf", "filled_form.pdf", cleaned_response[0])
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON response: {e}")
                print("Raw Gemini Response:")
                print(gemini_response_text)
        else:
            print("\nFailed to get a response from Gemini API.")

        if gemini_response_text:
            self.response = gemini_response_text
        else:
            self.response = None
        print("\nProcessing complete.")