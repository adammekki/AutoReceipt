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
import uuid
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

# In-memory session storage for verification workflow
# Maps session_id -> { temp_dir, extracted_data, instances, expires_at }
# NOTE: In production, you'd want a more robust session store with TTL
verification_sessions: Dict[str, Dict[str, Any]] = {}

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


class ExtractedDataResponse(BaseModel):
    """Response model for extraction endpoint - returns data for verification."""
    status: str
    message: str
    session_id: Optional[str] = None
    hinreise: Optional[Dict[str, Any]] = None
    ruckreise: Optional[Dict[str, Any]] = None
    hotel: Optional[Dict[str, Any]] = None
    errors: Optional[List[str]] = None


class VerifiedDataRequest(BaseModel):
    """Request model for submitting verified data."""
    session_id: str
    hinreise: Dict[str, Any]
    ruckreise: Dict[str, Any]
    hotel: Dict[str, Any]


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


@app.post("/api/extract-trip", response_model=ExtractedDataResponse)
async def extract_trip(
    # Antrag Upload
    antrag_form: UploadFile = File(..., description="Dienstreiseantrag PDF form"),

    # Flight receipts (any number)
    flight_receipts: List[UploadFile] = File([], description="Any number of flight receipts"),

    # Hotel / Conference receipts
    hotel_receipts: List[UploadFile] = File([], description="Any number of hotel or conference receipts"),

    # User profile data for prefilling (optional)
    user_profile: Optional[str] = Form(None, description="User profile JSON for prefilling form fields"),
):
    """
    Extract data from trip documents without filling PDF.
    
    This endpoint processes uploaded receipts through the AI pipeline
    and returns extracted data for user verification before final PDF generation.
    
    Returns a session_id to be used with /api/submit-verified.
    """
    errors = []
    session_id = str(uuid.uuid4())
    
    # Create a persistent temporary directory for this session
    temp_dir = tempfile.mkdtemp(prefix=f"autoreceipt_{session_id}_")
    
    # Create separate subdirectories for flight and hotel receipts
    flight_dir = os.path.join(temp_dir, "flights")
    hotel_dir = os.path.join(temp_dir, "hotels")
    os.makedirs(flight_dir, exist_ok=True)
    os.makedirs(hotel_dir, exist_ok=True)
    
    try:
        # Save the Antrag form
        uploads_dir = os.path.join(HERE, "uploads")
        os.makedirs(uploads_dir, exist_ok=True)

        antrag_path = os.path.join(uploads_dir, "Dienstreiseantrag.pdf")
        contents = await antrag_form.read()
        with open(antrag_path, "wb") as f:
            f.write(contents)
        print(f"Saved Dienstreiseantrag to {antrag_path}")

        # Save flight receipts to flight_dir
        for i, file in enumerate(flight_receipts, start=1):
            if file is not None:
                filename = f"Receipt_Flight{i}.pdf"
                file_path = os.path.join(flight_dir, filename)
                try:
                    contents = await file.read()
                    with open(file_path, "wb") as f:
                        f.write(contents)
                    print(f"Saved {filename} to {file_path}")
                except Exception as e:
                    errors.append(f"Error saving {filename}: {str(e)}")
        
        # Save hotel receipts to hotel_dir
        for i, file in enumerate(hotel_receipts, start=1):
            if file is not None:
                filename = f"Receipt_Hotel{i}.pdf"
                file_path = os.path.join(hotel_dir, filename)
                try:
                    contents = await file.read()
                    with open(file_path, "wb") as f:
                        f.write(contents)
                    print(f"Saved {filename} to {file_path}")
                except Exception as e:
                    errors.append(f"Error saving {filename}: {str(e)}")
        
        # Parse user profile if provided
        parsed_user_profile: Optional[Dict[str, Any]] = None
        if user_profile:
            try:
                parsed_user_profile = json.loads(user_profile)
                print(f"Received user profile for prefill: {list(parsed_user_profile.keys())}")
                # Validate that no bank data is included
                forbidden_fields = ['bic', 'iban', 'kreditinstitut', 'bank']
                for field in forbidden_fields:
                    if field in [k.lower() for k in parsed_user_profile.keys()]:
                        print(f"WARNING: Rejecting forbidden field '{field}' from user profile")
                        parsed_user_profile.pop(field, None)
            except json.JSONDecodeError as e:
                print(f"Warning: Could not parse user profile JSON: {e}")
                parsed_user_profile = None
        
        # Run extraction pipeline (without PDF filling)
        try:
            # Step 1: Antrag processing
            print("Starting Antrag extraction...")
            antrag_instance = antrag(data_dir=temp_dir, user_profile=parsed_user_profile)
            antrag_instance.main()
            
            # Step 2: Hinreise extraction (without PDF fill) - uses flight receipts only
            print("Starting Hinreise extraction...")
            hinreise_instance = hinreise("", data_dir=flight_dir)
            hinreise_data = hinreise_instance.main(fill_pdf=False)
            
            # Step 3: Ruckreise extraction (without PDF fill) - uses flight receipts only
            print("Starting Ruckreise extraction...")
            ruckreise_instance = ruckreise(hinreise_instance.response, data_dir=flight_dir)
            ruckreise_data = ruckreise_instance.main(fill_pdf=False)
            
            # Step 4: Hotel extraction (without PDF fill) - uses hotel receipts only
            print("Starting Hotel extraction...")
            hotel_instance = hotel(data_dir=hotel_dir)
            hotel_data = hotel_instance.main(fill_pdf=False)
            
        except Exception as e:
            # Clean up on error
            shutil.rmtree(temp_dir, ignore_errors=True)
            errors.append(f"Pipeline processing error: {str(e)}")
            return ExtractedDataResponse(
                status="error",
                message="Failed to extract trip data",
                errors=errors
            )
        
        # Store session data for later verification submission
        verification_sessions[session_id] = {
            "temp_dir": temp_dir,
            "hinreise_instance": hinreise_instance,
            "ruckreise_instance": ruckreise_instance,
            "hotel_instance": hotel_instance,
            "extracted_data": {
                "hinreise": hinreise_data or {},
                "ruckreise": ruckreise_data or {},
                "hotel": hotel_data or {}
            }
        }
        
        print(f"Created verification session: {session_id}")
        print(f"Hotel data extracted: {len(hotel_data) if hotel_data else 0} fields")
        
        return ExtractedDataResponse(
            status="ok",
            message="Data extracted successfully. Please verify and submit.",
            session_id=session_id,
            hinreise=hinreise_data or {},
            ruckreise=ruckreise_data or {},
            hotel=hotel_data or {},
            errors=errors if errors else None
        )
        
    except Exception as e:
        # Clean up on error
        shutil.rmtree(temp_dir, ignore_errors=True)
        errors.append(f"Unexpected error: {str(e)}")
        return ExtractedDataResponse(
            status="error",
            message="An unexpected error occurred during extraction",
            errors=errors
        )


@app.post("/api/submit-verified", response_model=ProcessTripResponse)
async def submit_verified(request: VerifiedDataRequest):
    """
    Submit verified data and generate the final PDF.
    
    This endpoint takes user-verified data from the verification screen
    and generates the final filled PDF form.
    """
    errors = []
    session_id = request.session_id
    
    # Check if session exists
    if session_id not in verification_sessions:
        raise HTTPException(
            status_code=404,
            detail="Session not found or expired. Please restart the process."
        )
    
    session = verification_sessions[session_id]
    
    try:
        templates_dir = os.path.join(HERE, "templates")
        
        # Fill PDF with verified data
        print("Filling PDF with verified Hinreise data...")
        hinreise_instance = session["hinreise_instance"]
        # Fallback: Restore extracted_data from session if empty
        if not hinreise_instance.extracted_data:
            session_data = session.get('extracted_data', {}).get('hinreise', {})
            if session_data:
                print(f"FALLBACK: Restoring hinreise extracted_data from session ({len(session_data)} fields)")
                hinreise_instance.extracted_data = session_data
        hinreise_instance.fill_with_verified_data(request.hinreise)
        
        print("Filling PDF with verified Rückreise data...")
        ruckreise_instance = session["ruckreise_instance"]
        # Fallback: Restore extracted_data from session if empty
        if not ruckreise_instance.extracted_data:
            session_data = session.get('extracted_data', {}).get('ruckreise', {})
            if session_data:
                print(f"FALLBACK: Restoring ruckreise extracted_data from session ({len(session_data)} fields)")
                ruckreise_instance.extracted_data = session_data
        ruckreise_instance.fill_with_verified_data(request.ruckreise)
        
        print("Filling PDF with verified Hotel data...")
        hotel_instance = session["hotel_instance"]
        # Fallback: Restore extracted_data from session if empty
        if not hotel_instance.extracted_data:
            session_data = session.get('extracted_data', {}).get('hotel', {})
            if session_data:
                print(f"FALLBACK: Restoring hotel extracted_data from session ({len(session_data)} fields)")
                hotel_instance.extracted_data = session_data
        hotel_instance.fill_with_verified_data(request.hotel)
        
        # Check if filled form was created
        filled_form_path = os.path.join(templates_dir, "filled_form.pdf")
        if os.path.exists(filled_form_path):
            # Copy to output directory
            output_dir = os.path.join(HERE, "output")
            os.makedirs(output_dir, exist_ok=True)
            
            output_filename = "output_form.pdf"
            shutil.copy2(
                filled_form_path,
                os.path.join(output_dir, output_filename)
            )
            
            # Clean up
            uploads_dir = os.path.join(HERE, "uploads")
            if os.path.exists(uploads_dir):
                shutil.rmtree(uploads_dir)
                print("Cleaned up uploads directory.")

            if os.path.exists(filled_form_path):
                os.remove(filled_form_path)
            
            # Clean up session
            temp_dir = session.get("temp_dir")
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
            del verification_sessions[session_id]
            print(f"Cleaned up session: {session_id}")
            
            return ProcessTripResponse(
                status="ok",
                message="Verified data processed successfully",
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
        # Clean up session on error
        if session_id in verification_sessions:
            temp_dir = verification_sessions[session_id].get("temp_dir")
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
            del verification_sessions[session_id]
        return ProcessTripResponse(
            status="error",
            message="An unexpected error occurred",
            errors=errors
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
