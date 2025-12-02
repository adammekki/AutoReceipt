"""
AutoReceipt FastAPI Backend

This module provides the FastAPI application that exposes HTTP APIs
to run the travel expense receipt processing pipeline.
"""

import os
import shutil
import tempfile
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
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
    # Flight receipts
    receipt_flight1: Optional[UploadFile] = File(None, description="Receipt for flight 1"),
    receipt_flight2: Optional[UploadFile] = File(None, description="Receipt for flight 2"),
    receipt_flight3: Optional[UploadFile] = File(None, description="Receipt for flight 3"),
    receipt_parking: Optional[UploadFile] = File(None, description="Parking receipt"),
    # Hotel/Conference receipts
    payment_conference: Optional[UploadFile] = File(None, description="Conference payment receipt"),
    payment_parking: Optional[UploadFile] = File(None, description="Parking payment receipt"),
    receipt_conference: Optional[UploadFile] = File(None, description="Conference receipt"),
    receipt_hotel: Optional[UploadFile] = File(None, description="Hotel receipt"),
    # Required form templates
    dienstreiseantrag: UploadFile = File(..., description="Dienstreiseantrag PDF form (required)"),
    reisekostenabrechnung: UploadFile = File(..., description="Reisekostenabrechnung PDF template (required)"),
    # Optional parameters
    supervisor_name: Optional[str] = Form(None, description="Override supervisor name"),
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
            # Define file mappings for uploads
            file_mappings = {
                "Receipt_Flight1.pdf": receipt_flight1,
                "Receipt_Flight2.pdf": receipt_flight2,
                "Receipt_Flight3.pdf": receipt_flight3,
                "Receipt_Parking.pdf": receipt_parking,
                "Payment_Conference.pdf": payment_conference,
                "Payment_Parking.pdf": payment_parking,
                "Receipt_Conference.pdf": receipt_conference,
                "Receipt_Hotel(6persons).pdf": receipt_hotel,
                "Dienstreiseantrag_11_12_2023_V2.pdf": dienstreiseantrag,
                "Reisekostenabrechnung_28_05_2024.pdf": reisekostenabrechnung,
            }
            
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
                # Step 1: Antrag processing
                print("Starting Antrag process...")
                antrag_instance = antrag(data_dir=temp_dir)
                antrag_instance.main(supervisor_name=supervisor_name)
                
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
            filled_form_path = os.path.join(temp_dir, "filled_form.pdf")
            if os.path.exists(filled_form_path):
                # Copy to a permanent location for download
                # In production, you'd want to store this more permanently
                output_dir = os.path.join(os.path.dirname(__file__), "..", "output")
                os.makedirs(output_dir, exist_ok=True)
                
                import uuid
                output_filename = f"filled_form_{uuid.uuid4().hex[:8]}.pdf"
                output_path = os.path.join(output_dir, output_filename)
                shutil.copy2(filled_form_path, output_path)
                
                return ProcessTripResponse(
                    status="ok",
                    message="Trip expenses processed successfully",
                    filled_pdf=output_filename,
                    errors=errors if errors else None
                )
            else:
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


@app.get("/api/download/{filename}")
async def download_file(filename: str):
    """
    Download a generated PDF file.
    
    Args:
        filename: Name of the file to download
    """
    output_dir = os.path.join(os.path.dirname(__file__), "..", "output")
    file_path = os.path.join(output_dir, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/pdf"
    )


# Individual endpoints for each processing step (optional, for fine-grained control)

@app.post("/api/antrag")
async def process_antrag(
    dienstreiseantrag: UploadFile = File(...),
    reisekostenabrechnung: UploadFile = File(...),
    supervisor_name: Optional[str] = Form(None),
):
    """Process only the Antrag step."""
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Save required files
            dienstreise_path = os.path.join(temp_dir, "Dienstreiseantrag_11_12_2023_V2.pdf")
            reisekosten_path = os.path.join(temp_dir, "Reisekostenabrechnung_28_05_2024.pdf")
            
            contents = await dienstreiseantrag.read()
            with open(dienstreise_path, "wb") as f:
                f.write(contents)
            
            contents = await reisekostenabrechnung.read()
            with open(reisekosten_path, "wb") as f:
                f.write(contents)
            
            # Process
            antrag_instance = antrag(data_dir=temp_dir)
            antrag_instance.main(supervisor_name=supervisor_name)
            
            return {"status": "ok", "message": "Antrag processed successfully"}
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
