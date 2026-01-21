import os
import io
import json
import google.generativeai as genai
from dotenv import load_dotenv
from PIL import Image
from pdf2image import convert_from_path

class ruckreise:
    def __init__(self, response, data_dir: str = "."):
        """
        Initialize ruckreise with a response and data directory.
        
        Args:
            response: Response from hinreise processing
            data_dir: Directory where PDF files are located
        """
        self.response = response
        self.data_dir = data_dir
        self.extracted_data = {}  # Will be populated by main()
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
            print("No valid images could be prepared from the provided documents. Sending only prompt.")
            if len(contents) == 1:
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
        Main execution block for ruckreise processing.
        
        Returns:
            dict: Extracted data
        """
        # Gather all supported files from the data directory dynamically
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
        
        context = context = ""
        if self.response:
            context = f"{json.dumps(self.response, ensure_ascii=False)}\n"

        multi_doc_prompt = rf"""
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

            You are also given the Hinreise JSON output to help identify overlapping information and prevent duplication:
            {context}

            Output format:
            A JSON list containing exactly one JSON object with the following UTF-16 encoded keys:

            Required Fields for the receipt:
               Required Fields for the receipt:
                - "þÿ\u0000R\u0000ü\u0000c\u0000k\u0000r\u0000e\u0000i\u0000s\u0000e\u0000 \u0000v\u0000o\u0000n": "(Origin city/location of the return journey, e.g., 'Bangkok')"
                - "þÿ\u0000R\u0000ü\u0000c\u0000k\u0000r\u0000e\u0000i\u0000s\u0000e\u0000 \u0000n\u0000a\u0000c\u0000h": "(Destination city/location of the return journey, e.g., 'Blaustein-Arnegg')"
                - "þÿ\u0000R\u0000ü\u0000c\u0000k\u0000r\u0000e\u0000i\u0000s\u0000e\u0000 \u0000a\u0000m": "(Start date of the return journey, format: DD.MM.YYYY, e.g., '22.12.2024')"
                - "þÿ\u0000R\u0000ü\u0000c\u0000k\u0000r\u0000e\u0000i\u0000s\u0000e\u0000 \u0000U\u0000h\u0000r\u0000z\u0000e\u0000i\u0000t": "(Start time of the return journey, format: HH:MM, e.g., '23:30')"
                - "þÿ\u0000R\u0000ü\u0000c\u0000k\u0000r\u0000e\u0000i\u0000s\u0000e\u0000 \u0000E\u0000n\u0000d\u0000e\u0000 \u0000a\u0000m": "(End date of the return journey, format: DD.MM.YYYY, e.g., '23.12.2024')"
                - "þÿ\u0000R\u0000ü\u0000c\u0000k\u0000r\u0000e\u0000i\u0000s\u0000e\u0000 \u0000E\u0000n\u0000d\u0000e\u0000 \u0000U\u0000h\u0000r\u0000z\u0000e\u0000i\u0000t": "(End time of the return journey, format: HH:MM, e.g., '10:00')"
                - "Rückreise_Ort": "(Specific location of arrival, e.g., 'Wohnung', 'Dienststelle')"
                - "Verkehrsmittel Rückreise": "(Primary mode of transport, e.g., 'Flugzeug', 'Bahn', 'Eigenes_KfZ', 'Fahrgemeinschaft', 'Bus_Bahn_Strassenbahn', 'Schiff', 'Sonstiges')"
                - "Klasse Rückreise": "(Class of travel, choices are 'Klasse 1', 'Klasse 2'. Leave empty if not specified)"
                - "þÿ\u0000F\u0000l\u0000u\u0000g\u0000z\u0000e\u0000u\u0000g\u0000_\u0000R\u0000ü\u0000c\u0000k\u0000r\u0000e\u0000i\u0000s\u0000e": "(Cost for air travel on the return journey. If both Hin- and Rückflug on one receipt, divide by 2. Format: '717,31€'). This cannot be left empty."
                - "þÿ\u0000B\u0000a\u0000h\u0000n\u0000_\u00001\u0000u\u00002\u0000_\u0000K\u0000l\u0000a\u0000s\u0000s\u0000e\u0000_\u0000R\u0000ü\u0000c\u0000k\u0000r\u0000e\u0000i\u0000s\u0000e": "(Cost for train travel on the return journey, e.g., '44,00€' or '1. Klasse')"
                - "þÿ\u0000E\u0000i\u0000g\u0000e\u0000n\u0000e\u0000s\u0000_\u0000K\u0000f\u0000Z\u0000_\u0000R\u0000ü\u0000c\u0000k\u0000r\u0000e\u0000i\u0000s\u0000e": "(Details for personal car usage, e.g., '174km')"
                - "þÿ\u0000D\u0000i\u0000e\u0000n\u0000s\u0000t\u0000w\u0000a\u0000g\u0000e\u0000n\u0000_\u0000R\u0000ü\u0000c\u0000k\u0000r\u0000e\u0000i\u0000s\u0000e": "(Details for company car usage)"
                - "þÿ\u0000F\u0000a\u0000h\u0000r\u0000g\u0000e\u0000m\u0000e\u0000i\u0000n\u0000s\u0000c\u0000h\u0000a\u0000f\u0000t\u0000_\u0000R\u0000ü\u0000c\u0000k\u0000r\u0000e\u0000i\u0000s\u0000e": "(If part of a carpool for the return journey, e.g., 'Fahrgemeinschaft')"
                - "þÿ\u0000S\u0000o\u0000n\u0000s\u0000t\u0000i\u0000g\u0000e\u0000s\u0000_\u0000R\u0000ü\u0000c\u0000k\u0000r\u0000e\u0000i\u0000s\u0000e": "(Any other relevant notes or costs for the return journey, e.g., 'Taxi 25€')"
                - "þÿ\u0000B\u0000u\u0000s\u0000_\u0000B\u0000a\u0000h\u0000n\u0000_\u0000S\u0000t\u0000r\u0000a\u0000ß\u0000e\u0000n\u0000b\u0000a\u0000h\u0000n\u0000_\u0000R\u0000ü\u0000c\u0000k\u0000r\u0000e\u0000i\u0000s\u0000e": "(Cost for local transport on the return journey, e.g., '15,00€ (Parken)')"
                - "þÿ\u0000S\u0000c\u0000h\u0000w\u0000e\u0000r\u0000b\u0000e\u0000s\u0000c\u0000h\u0000ä\u0000d\u0000i\u0000g\u0000t\u0000_\u0000R\u0000ü\u0000c\u0000k\u0000r\u0000e\u0000i\u0000s\u0000e": "(If the traveler is severely disabled for the return journey)"
        """


        print("\nSending requests to Gemini API for Rückreise extraction...")
        gemini_response_text = self.get_gemini_vision_response_multi_doc(all_document_paths, multi_doc_prompt)

        extracted_data = {}
        if gemini_response_text:
            print("\nGemini API Response:")
            cleaned_response = gemini_response_text.strip('```json\n').strip('\n```')
            try:
                parsed_response = json.loads(cleaned_response)
                extracted_data = parsed_response[0] if parsed_response else {}
                print(json.dumps(extracted_data, indent=2, ensure_ascii=False))
                
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON response: {e}")
                print("Raw Gemini Response:")
                print(gemini_response_text)
                extracted_data = {}
        else:
            print("\nFailed to get a response from Gemini API.")
            extracted_data = {}

        self.extracted_data = extracted_data
        print("\nRuckreise Processing complete.")
        
        return extracted_data