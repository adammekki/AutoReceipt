import os
import io
import json
import google.generativeai as genai
from dotenv import load_dotenv
from PIL import Image
from pdf2image import convert_from_path

class hotel:
    """
    Simple hotel/conference data extractor.
    Extracts data from receipts using Gemini and fills PDF forms directly.
    """

    def __init__(self, data_dir: str = "."):
        """
        Initialize hotel with a data directory.
        
        Args:
            data_dir: Directory where receipt files are located
        """
        self.data_dir = data_dir
        self.extracted_data = {}
        self._setup_gemini()

    def _setup_gemini(self):
        """Setup Gemini API configuration."""
        load_dotenv()
        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        if not self.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not found in environment variables. Please set it in your .env file.")
        genai.configure(api_key=self.GEMINI_API_KEY)

    def prepare_document_for_gemini(self, document_path):
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
                poppler_path = os.getenv("POPPLER_PATH")
                if poppler_path:
                    images_from_pdf = convert_from_path(document_path, poppler_path=poppler_path)
                else:
                    images_from_pdf = convert_from_path(document_path)
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

    def get_gemini_vision_response_multi_doc(self, document_paths_list, prompt):
        """Send multiple documents to Gemini API with a prompt."""
        model = genai.GenerativeModel('gemini-3-flash-preview')

        contents = [prompt]
        all_image_parts = []

        for doc_path in document_paths_list:
            prepared_parts = self.prepare_document_for_gemini(doc_path)
            all_image_parts.extend(prepared_parts)

        if not all_image_parts:
            print("No valid images could be prepared from the provided documents.")
            return None
            
        contents.extend(all_image_parts)

        try:
            response = model.generate_content(contents)
            return response.text
        except Exception as e:
            print(f"Error calling Gemini API with documents: {e}")
            return None

    def main(self):
        """
        Main execution block for hotel processing.
        
        Returns:
            dict: Extracted data (always returned for API compatibility)
        """
        # Gather all supported files from the data directory
        allowed_exts = {'.pdf', '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'}
        all_document_paths = []
        
        if not os.path.isdir(self.data_dir):
            print(f"Data directory not found: {self.data_dir}")
        else:
            for entry in sorted(os.listdir(self.data_dir)):
                path = os.path.join(self.data_dir, entry)
                if os.path.isfile(path):
                    ext = os.path.splitext(entry)[1].lower()
                    if ext in allowed_exts:
                        all_document_paths.append(path)

        if not all_document_paths:
            print(f"No supported documents found in {self.data_dir}")
            self.extracted_data = {}
            return {}

        FIELD_NAMES = {
            "geschaeftsort_am": "\u00fe\u00ff\u0000G\u0000e\u0000s\u0000c\u0000h\u0000\u00e4\u0000f\u0000t\u0000s\u0000o\u0000r\u0000t\u0000_\u0000a\u0000m",
            "geschaeftsort_uhrzeit": "\u00fe\u00ff\u0000G\u0000e\u0000s\u0000c\u0000h\u0000\u00e4\u0000f\u0000t\u0000s\u0000o\u0000r\u0000t\u0000_\u0000U\u0000h\u0000r\u0000z\u0000e\u0000i\u0000t",
            "dienstgeschaeft_am": "\u00fe\u00ff\u0000D\u0000i\u0000e\u0000n\u0000s\u0000t\u0000g\u0000e\u0000s\u0000c\u0000h\u0000\u00e4\u0000f\u0000t\u0000_\u0000a\u0000m",
            "dienstgeschaeft_um": "\u00fe\u00ff\u0000D\u0000i\u0000e\u0000n\u0000s\u0000t\u0000g\u0000e\u0000s\u0000c\u0000h\u0000\u00e4\u0000f\u0000t\u0000_\u0000u\u0000m",
            "ende_dienstgeschaeft_am": "\u00fe\u00ff\u0000E\u0000n\u0000d\u0000e\u0000_\u0000D\u0000i\u0000e\u0000n\u0000s\u0000t\u0000g\u0000e\u0000s\u0000c\u0000h\u0000\u00e4\u0000f\u0000t\u0000_\u0000a\u0000m",
            "ende_dienstgeschaeft_um": "\u00fe\u00ff\u0000E\u0000n\u0000d\u0000e\u0000_\u0000D\u0000i\u0000e\u0000n\u0000s\u0000t\u0000g\u0000e\u0000s\u0000c\u0000h\u0000\u00e4\u0000f\u0000t\u0000_\u0000u\u0000m",
            "kosten_unterkunft": "\u00fe\u00ff\u0000G\u0000e\u0000s\u0000c\u0000h\u0000\u00e4\u0000f\u0000t\u0000s\u0000k\u0000o\u0000r\u0000t\u0000_\u0000K\u0000o\u0000s\u0000t\u0000e\u0000n\u0000_\u0000U\u0000n\u0000t\u0000e\u0000r\u0000k\u0000u\u0000n\u0000f\u0000t",
            "sonstige_kosten": "\u00fe\u00ff\u0000G\u0000e\u0000s\u0000c\u0000h\u0000\u00e4\u0000f\u0000t\u0000s\u0000k\u0000o\u0000r\u0000t\u0000_\u0000s\u0000o\u0000n\u0000s\u0000t\u0000i\u0000g\u0000e\u0000_\u0000K\u0000o\u0000s\u0000t\u0000e\u0000n",
            "bus_geschaeftsort": "Bus Gesch\u00e4ftsort",
            "fahrtkosten_bahn": "\u00fe\u00ff\u0000G\u0000e\u0000s\u0000c\u0000h\u0000\u00e4\u0000f\u0000t\u0000s\u0000k\u0000o\u0000r\u0000t\u0000_\u0000F\u0000a\u0000h\u0000r\u0000t\u0000k\u0000o\u0000s\u0000t\u0000e\u0000n\u0000_\u0000B\u0000a\u0000h\u0000n\u0000_\u0000S\u0000t\u0000r\u0000a\u0000\u00df\u0000e\u0000n\u0000b\u0000a\u0000h\u0000n",
            "sonstige_geschaeftsort": "Sonstige Gesch\u00e4ftsort",
            "fahrtkosten_sonstiges": "\u00fe\u00ff\u0000G\u0000e\u0000s\u0000c\u0000h\u0000\u00e4\u0000f\u0000t\u0000s\u0000k\u0000o\u0000r\u0000t\u0000_\u0000F\u0000a\u0000h\u0000r\u0000t\u0000k\u0000o\u0000s\u0000t\u0000e\u0000n\u0000_\u0000s\u0000o\u0000n\u0000s\u0000t\u0000i\u0000g\u0000e\u0000s",
        }

        multi_doc_prompt = rf"""
        You are an expert at extracting travel expense details from receipts. You will be provided with one or more document images (converted from original images or PDF pages). For each document, extract the following information and return it as a JSON object within a list. The JSON keys MUST exactly match the specified field names below. If a field cannot be found or is not applicable for a specific receipt, return its value as null for that receipt. For amounts, extract the numerical value followed by the currency symbol. If there are several documents, infer the data that is likely to be connected and merge them together into one output. Instead of using None, use empty string.
        Date format: DD.MM.YYYY
        Time format: HH:MM (24-hour format)
        If the receipt only covers the flights, ignore it.

        Output format: A JSON list where each element is a JSON object representing one receipt's extracted data.

        Required Fields for the receipt:
        - "geschaeftsort_am": This is the date of arrival of the conference venue, here, put the date of arrival of the hotel.
        - "geschaeftsort_uhrzeit": This is the time of arrival of the conference venue, here, put the time of arrival of the hotel, or the check-in time for the hotel. If both are not available, put in 15:00.
        - "dienstgeschaeft_am": This is the start date of the conference.
        - "dienstgeschaeft_um": This is the start time of the conference.
        - "ende_dienstgeschaeft_am": This is the end date of the conference.
        - "ende_dienstgeschaeft_um": This is the end time of the conference.
        - "kosten_unterkunft": This is the costs for accommodation including breakfast (if included). If the room capacity is more than one person, divide the total cost by the number of persons to get the correct amount. THIS CANNOT BE LEFT EMPTY. This should have a euros currency symbol.
        - "sonstige_kosten": This is other costs (e.g. conference fee, parking fees...). This should be in euros, but if other currency is used, specify it. Make sure to specify the currency symbol of the amount.
        - "bus_geschaeftsort": This is a checkbox field, if bus or tram (Straßenbahn) is used for business travel, put "ja", else put "nein" (no other options).
        - "fahrtkosten_bahn": This is the costs for train or tram (Straßenbahn) tickets.
        - "sonstige_geschaeftsort": This is a checkbox field, if other means of transport (e.g. taxi) is used for business travel, put "ja", else put "nein" (no other options).
        - "fahrtkosten_sonstiges": This is the costs for other means of transport (e.g. taxi).
        """

        print("\nSending requests to Gemini API for Hotel extraction...")
        gemini_response_text = self.get_gemini_vision_response_multi_doc(all_document_paths, multi_doc_prompt)

        if gemini_response_text:
            print("\nGemini API Response:")
            cleaned_response = gemini_response_text.strip('```json\n').strip('\n```')
            try:
                parsed_response = json.loads(cleaned_response)
                gemini_data = parsed_response[0] if parsed_response else {}
                print(json.dumps(gemini_data, indent=2, ensure_ascii=False))
                
                # Map Gemini's simple keys to the actual PDF field names
                self.extracted_data = {}
                for simple_key, pdf_key in FIELD_NAMES.items():
                    if simple_key in gemini_data:
                        self.extracted_data[pdf_key] = gemini_data[simple_key]
                
                print("\nMapped to PDF fields:")
                print(json.dumps(self.extracted_data, indent=2, ensure_ascii=False))
                
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON response: {e}")
                print("Raw Gemini Response:")
                print(gemini_response_text)
                self.extracted_data = {}
        else:
            print("\nFailed to get a response from Gemini API.")
            self.extracted_data = {}

        print("\nHotel Processing complete.")
        return self.extracted_data