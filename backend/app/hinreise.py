import os
import io
import json
import google.generativeai as genai
from dotenv import load_dotenv
from PIL import Image
from pdf2image import convert_from_path


class hinreise:
    def __init__(self, data_dir: str = "."):
        """
        Initialize hinreise with a data directory.
        
        Args:
            data_dir: Directory where PDF files are located
        """
        self.data_dir = data_dir
        self.extracted_data = {}  # Will be populated by main()
        self.cached_image_parts = []  # Cache converted images for reuse by ruckreise
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

    def prepare_all_documents(self, document_paths_list):
        """
        Prepare all documents and cache the image parts for reuse.
        
        Args:
            document_paths_list: List of paths to documents
            
        Returns:
            list: All prepared image parts
        """
        all_image_parts = []
        for doc_path in document_paths_list:
            prepared_parts = self.prepare_document_for_gemini(doc_path)
            all_image_parts.extend(prepared_parts)
        
        # Cache for reuse by ruckreise
        self.cached_image_parts = all_image_parts
        return all_image_parts

    def get_gemini_vision_response(self, image_parts, prompt):
        """
        Send prepared image parts to Gemini API with a prompt.
        
        Args:
            image_parts: Pre-prepared Gemini-compatible image parts
            prompt: The prompt to send
            
        Returns:
            str: Gemini response text
        """
        model = genai.GenerativeModel('gemini-3-flash-preview')

        contents = [prompt]

        if not image_parts:
            print("No valid images provided. Sending only prompt.")
            return None
            
        contents.extend(image_parts)

        try:
            response = model.generate_content(contents)
            return response.text
        except Exception as e:
            print(f"Error calling Gemini API with documents: {e}")
            return None

    def main(self):
        """
        Main execution block for hinreise processing.
        Extracts data from documents for verification.
        
        Returns:
            dict: Extracted data for user verification.
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
            self.response = None
            self.cached_image_parts = []
            return {}

        # Prepare all documents and cache for reuse by ruckreise
        print("\nPreparing documents for Gemini API...")
        image_parts = self.prepare_all_documents(all_document_paths)
        
        if not image_parts:
            print("No valid images could be prepared from the provided documents.")
            self.extracted_data = {}
            self.response = None
            return {}

        multi_doc_prompt = """
        You are an expert at extracting travel expense details from receipts. You will be provided with one or more document images (converted from original images or PDF pages). For each document, extract the following information and return it as a JSON object within a list. The JSON keys MUST exactly match the specified field names below. If a field cannot be found or is not applicable for a specific receipt, return its value as empty string for that receipt. For amounts, extract the numerical value followed by the currency symbol. If there are several documents, infer the data that is likely to be connected and merge them together into one output.

        If a receipt represents both the outbound and return journeys (e.g., a roundtrip flight ticket covering both Hin- und Rückflug), **split the cost evenly** between Hinreise and Rückreise, dividing the total by two.

        Output format: A JSON list where each element is a JSON object representing one receipt's extracted data.

        Required Fields for the receipt:
        - Hinreise_von: (Origin city/location of the outbound journey, e.g., "Blaustein-Arnegg")
        - Hinreise_nach: (Destination city/location of the outbound journey, e.g., "Bangkok")
        - Hinreise_Beginn: (Start date of the outbound journey, format: DD.MM.YYYY, e.g., "12.12.2024")
        - Hinreise_Uhrzeit: (Start time of the outbound journey, format: HH:MM, e.g., "17:00")
        - Hinreise_Ort: (Specific location of departure, either 'Wohnung', 'Dienststelle')
        - Hinreise_Urlaubsort: (If the outbound journey ends at a vacation spot before the official trip, otherwise empty string)
        - Verkehrsmittel Hinreise: (Primary mode of transport for the outbound journey, e.g., "Flugzeug", "Bahn", "Eigenes_KfZ", "Fahrgemeinschaft", "Bus_Bahn_Strassenbahn", "Schiff", "Sonstiges")
        - Klasse Hinreise: (Class of travel if applicable, either 'Klasse 2', 'Klasse 1'. If not specified, use empty string.)
        - Flugzeug_Hinreise: (Cost for air travel on the outbound journey. Extract numerical value followed by currency symbol, e.g., "1234,56€". This can not be left empty)
        - Bahn_1u2_Klasse_Hinreise: (Cost for train travel on the outbound journey, including class details. Extract numerical value followed by currency symbol, e.g., "44,00€" or "1. Klasse")
        - Eigenes_KfZ_Hinreise: (Details for personal car usage on the outbound journey. Extract distance in km and any parking notes, e.g., "88km Parken Freising")
        - Dienstwagen_Hinreise: (Details for company car usage on the outbound journey, if applicable. Otherwise empty string.)
        - Fahrgemeinschaft Hinreise: (If part of a carpool for the outbound journey, state "Fahrgemeinschaft". Otherwise empty string.)
        - Sonstiges_Hinreise: (Any other relevant notes or costs for the outbound journey not covered by specific transport fields, e.g., "(Hin- und Rückflug)", "Taxi 25€")
        - Bus_Bahn_Strassenbahn_Hinreise: (Cost for bus, tram, or local train travel on the outbound journey. Extract numerical value followed by currency symbol and any notes, e.g., "67,00€ (Parken)", do not put the flight cost here)
        - planmäßige_Abfahrt: "(If the outbound journey's departure was scheduled on time, otherwise empty string).
        - Schwerbeschädigt Hinreise: '(If the traveler is severely disabled for the outbound journey, otherwise empty string).
        """

        print("\nSending request to Gemini API for Hinreise extraction...")
        gemini_response_text = self.get_gemini_vision_response(image_parts, multi_doc_prompt)

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

        self.response = gemini_response_text
        self.extracted_data = extracted_data
        print("\nHinreise Processing complete.")
        
        return extracted_data