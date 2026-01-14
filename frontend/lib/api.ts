const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface ExtractedDataResponse {
  status: string;
  message: string;
  session_id: string;
  hinreise: Record<string, string>;
  ruckreise: Record<string, string>;
  hotel: Record<string, string>;
  errors?: string[];
}

export interface SubmitVerifiedRequest {
  session_id: string;
  hinreise: Record<string, string>;
  ruckreise: Record<string, string>;
  hotel: Record<string, string>;
}

export interface ProcessTripResponse {
  status: string;
  message: string;
  filled_pdf?: string;
  errors?: string[];
}

export interface UserProfile {
  name?: string;
  personalNumber?: string;
  costCenter?: string;
  department?: string;
  email?: string;
  phone?: string;
}

/**
 * Extract trip data from uploaded documents.
 * Sends documents to the backend for AI processing and returns extracted data for verification.
 */
export async function extractTripData(
  antragForm: File,
  flightReceipts: File[],
  hotelReceipts: File[],
  userProfile?: UserProfile | null
): Promise<ExtractedDataResponse> {
  const formData = new FormData();
  
  // Add the Antrag form (required)
  formData.append('antrag_form', antragForm);
  
  // Add flight receipts
  flightReceipts.forEach((file) => {
    formData.append('flight_receipts', file);
  });
  
  // Add hotel/conference receipts
  hotelReceipts.forEach((file) => {
    formData.append('hotel_receipts', file);
  });
  
  // Add user profile if provided
  if (userProfile) {
    formData.append('user_profile', JSON.stringify(userProfile));
  }
  
  const response = await fetch(`${API_BASE_URL}/api/extract-trip`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Extraction failed: ${response.status} - ${errorText}`);
  }

  return response.json();
}

/**
 * Submit verified data to generate the final filled PDF.
 */
export async function submitVerifiedData(
  data: SubmitVerifiedRequest
): Promise<ProcessTripResponse> {
  const response = await fetch(`${API_BASE_URL}/api/submit-verified`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Submission failed: ${response.status} - ${errorText}`);
  }

  return response.json();
}

/**
 * Download the filled PDF form from the backend.
 * @returns A Blob containing the PDF file
 */
export async function downloadFilledForm(): Promise<Blob> {
  const response = await fetch(`${API_BASE_URL}/api/download`, {
    method: 'GET',
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Download failed: ${response.status} - ${errorText}`);
  }

  return response.blob();
}
