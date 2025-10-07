import os
import google.generativeai as genai
from dotenv import load_dotenv
from PIL import Image
import io
import json
from fillform import PdfWrapper

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables. Please set it in your .env file.")

genai.configure(api_key=GEMINI_API_KEY)

def get_gemini_vision_response(image_path, prompt):
    model = genai.GenerativeModel('gemini-2.5-flash')

    try:
        img = Image.open(image_path)
    except FileNotFoundError:
        print(f"Error: Image file not found at {image_path}")
        return None
    except Exception as e:
        print(f"Error loading image: {e}")
        return None

    img_byte_arr = io.BytesIO()
    image_format = img.format if img.format else 'JPEG'
    img.save(img_byte_arr, format=image_format)
    img_byte_arr = img_byte_arr.getvalue()

    contents = [
        prompt,
        {
            'mime_type': f'image/{image_format.lower()}', # e.g., 'image/jpeg' or 'image/png'
            'data': img_byte_arr
        }
    ]

    try:
        response = model.generate_content(contents)
        return response.text
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return None

if __name__ == "__main__":

    receipt_prompt = """
    You are an expert at extracting expense details from receipts. Extract the following information from the provided receipt image and return it as a JSON object. If a field is not found, return its value as null.

    Required Fields:
    - date (format: YYYY-MM-DD)
    - amount (numerical value, without currency symbol)
    - currency (e.g., USD, EUR, GBP)
    - merchant_name (name of the store/vendor)
    - category (e.g., travel, accommodation, food, supplies - infer if not explicit, use "other" if unsure)
    - description (brief description of the expense, if available)

    Return the output strictly in JSON format.
    """

    print("\nSending request to Gemini API...")
    gemini_response = get_gemini_vision_response("test_receipt2.jpeg", receipt_prompt)

    if gemini_response:
        print("\nGemini API Response:")
        print(gemini_response)
    else:
        print("\nFailed to get a response from Gemini API.")