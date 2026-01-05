"""
AutoReceipt FastAPI Backend

This module provides the FastAPI application that exposes HTTP APIs
to run the travel expense receipt processing pipeline.

PRIVACY CONSTRAINTS (STRICT):
- No user data may be stored on the server beyond request scope
- No receipts or documents may be persisted
- No bank data may be stored
- User profile data is only used within the request and then discarded
- This is a hard requirement due to GDPR and thesis design constraints
"""

import os
import json
import shutil
import tempfile
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, UploadFile, File, HTTPException, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import business logic modules
from app.antrag import antrag
from app.hinreise import hinreise
from app.ruckreise import ruckreise
from app.hotel import hotel

HERE = os.path.dirname(__file__)

# Initialize FastAPI app
app = FastAPI(
    title="AutoReceipt API",
    description="API for automated travel expense receipt processing using AI",
    version="1.0.0"
)

# Configure CORS for local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js default dev server
        "http://127.0.0.1:3000",
        "http://localhost:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ProcessTripResponse(BaseModel):
    """Response model for the process-trip endpoint."""
    status: str
    message: str
    filled_pdf: Optional[str] = None
    errors: Optional[List[str]] = None


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    message: str


@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint returning API health status."""
    return HealthResponse(
        status="ok",
        message="AutoReceipt API is running"
    )


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="ok",
        message="AutoReceipt API is healthy"
    )


@app.post("/api/process-trip", response_model=ProcessTripResponse)
async def process_trip(

    # Antrag Upload
    antrag_form: UploadFile = File(..., description="Dienstreiseantrag PDF form"),

    # Flight receipts (any number)
    flight_receipts: List[UploadFile] = File([], description="Any number of flight receipts"),

    # Hotel / Conference receipts
    hotel_receipts: List[UploadFile] = File([], description="Any number of hotel or conference receipts"),

    # User profile data for prefilling (optional)
    # Sent as JSON string to be parsed
    user_profile: Optional[str] = Form(None, description="User profile JSON for prefilling form fields"),

):
    """
    Process a complete trip expense report.
    
    This endpoint accepts uploaded PDF receipts, processes them through
    the AI pipeline (Gemini), and generates a filled expense report PDF.
    
    Required files:
    - dienstreiseantrag: The Dienstreiseantrag PDF form with applicant data
    - reisekostenabrechnung: The Reisekostenabrechnung template to fill
    
    Optional receipts:
    - receipt_flight1, receipt_flight2, receipt_flight3: Flight receipts
    - receipt_parking: Parking receipt
    - payment_conference, receipt_conference: Conference-related receipts
    - payment_parking: Parking payment
    - receipt_hotel: Hotel receipt
    """
    errors = []
    
    # Create a temporary directory for processing
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Save the Antrag form the uploads dir
            uploads_dir = os.path.join(HERE, "uploads")
            templates_dir = os.path.join(HERE, "templates")
            os.makedirs(uploads_dir, exist_ok=True)

            antrag_path = os.path.join(uploads_dir, "Dienstreiseantrag.pdf")
            contents = await antrag_form.read()
            with open(antrag_path, "wb") as f:
                f.write(contents)
            print(f"Saved Dienstreiseantrag to {antrag_path}")

            # Define file mappings for uploads
            file_mappings = {}

            for i, file in enumerate(flight_receipts, start=1):
                file_mappings[f"Receipt_Flight{i}.pdf"] = file

            for i, file in enumerate(hotel_receipts, start=1):
                file_mappings[f"Receipt_Hotel{i}.pdf"] = file
            
            # Save uploaded files to temp directory
            for filename, upload_file in file_mappings.items():
                if upload_file is not None:
                    file_path = os.path.join(temp_dir, filename)
                    try:
                        contents = await upload_file.read()
                        with open(file_path, "wb") as f:
                            f.write(contents)
                        print(f"Saved {filename} to {file_path}")
                    except Exception as e:
                        errors.append(f"Error saving {filename}: {str(e)}")
            
            # Run the processing pipeline
            try:
                # Parse user profile if provided
                # PRIVACY: This data is used only within this request scope
                # and is never persisted to any storage
                parsed_user_profile: Optional[Dict[str, Any]] = None
                if user_profile:
                    try:
                        parsed_user_profile = json.loads(user_profile)
                        print(f"Received user profile for prefill: {list(parsed_user_profile.keys())}")
                        # Validate that no bank data is included (extra safety check)
                        forbidden_fields = ['bic', 'iban', 'kreditinstitut', 'bank']
                        for field in forbidden_fields:
                            if field in [k.lower() for k in parsed_user_profile.keys()]:
                                print(f"WARNING: Rejecting forbidden field '{field}' from user profile")
                                parsed_user_profile.pop(field, None)
                    except json.JSONDecodeError as e:
                        print(f"Warning: Could not parse user profile JSON: {e}")
                        parsed_user_profile = None
                
                # Step 1: Antrag processing with user profile prefill
                print("Starting Antrag process...")
                antrag_instance = antrag(data_dir=temp_dir, user_profile=parsed_user_profile)
                antrag_instance.main()
                
                # Step 2: Hinreise processing
                print("Starting Hinreise process...")
                hinreise_instance = hinreise("", data_dir=temp_dir)
                hinreise_instance.main()
                
                # Step 3: Ruckreise processing
                print("Starting Ruckreise process...")
                ruckreise_instance = ruckreise(hinreise_instance.response, data_dir=temp_dir)
                ruckreise_instance.main()
                
                # Step 4: Hotel processing
                print("Starting Hotel process...")
                hotel_instance = hotel(data_dir=temp_dir)
                hotel_instance.main()
                
            except Exception as e:
                errors.append(f"Pipeline processing error: {str(e)}")
                return ProcessTripResponse(
                    status="error",
                    message="Failed to process trip expenses",
                    errors=errors
                )
            
            # Check if filled form was created
            filled_form_path = os.path.join(templates_dir, "filled_form.pdf")
            if os.path.exists(filled_form_path):
                # Copy to a permanent location for download
                # In production, you'd want to store this more permanently
                output_dir = os.path.join(HERE, "output")
                os.makedirs(output_dir, exist_ok=True)
                
                output_filename = "output_form.pdf"
                shutil.copy2(
                    os.path.join(templates_dir, "filled_form.pdf"),
                    os.path.join(output_dir, output_filename)
                )
                # Clean up uploads directory
                if os.path.exists(uploads_dir):
                    shutil.rmtree(uploads_dir)
                    print("Cleaned up uploads directory.")

                if os.path.exists(os.path.join(templates_dir, "filled_form.pdf")):
                    os.remove(os.path.join(templates_dir, "filled_form.pdf"))
                
                return ProcessTripResponse(
                    status="ok",
                    message="Trip expenses processed successfully",
                    filled_pdf=output_filename,
                    errors=errors if errors else None
                )
            else:
                # Clean up uploads directory
                if os.path.exists(uploads_dir):
                    shutil.rmtree(uploads_dir)
                    print("Cleaned up uploads directory.")

                if os.path.exists(os.path.join(templates_dir, "filled_form.pdf")):
                    os.remove(os.path.join(templates_dir, "filled_form.pdf"))

                errors.append("Filled form was not generated")
                return ProcessTripResponse(
                    status="error",
                    message="Processing completed but filled form was not generated",
                    errors=errors
                )
                
        except Exception as e:
            errors.append(f"Unexpected error: {str(e)}")
            return ProcessTripResponse(
                status="error",
                message="An unexpected error occurred",
                errors=errors
            )


@app.get("/api/download")
async def download_filled_form(background_tasks: BackgroundTasks):
    """
    Download a generated PDF file.
    
    Args:
        filename: Name of the file to download
    """
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    file_path = os.path.join(output_dir, "output_form.pdf")
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    # Schedule cleanup after response is sent
    def cleanup_output():
        try:
            if os.path.exists(output_dir):
                shutil.rmtree(output_dir)
                print("Cleaned up output directory")
        except Exception as e:
            print(f"Error cleaning up output directory: {e}")
    
    background_tasks.add_task(cleanup_output)
    
    return FileResponse(
        path=file_path,
        filename="output_form.pdf",
        media_type="application/pdf"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
