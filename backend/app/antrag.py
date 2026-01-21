"""
Antrag Processing Module

This module handles the extraction of user data from the Dienstreiseantrag (travel request form)
and uses it to prefill the Reisekostenabrechnung (expense report) form.

PREFILL PRIORITY LOGIC:
1. Primary source: User profile data received from the frontend
2. Secondary source: Extracted values from the Antrag document
3. Final state: Fields already populated from the profile MUST NOT be overwritten

This ensures:
- Reduced manual entry
- Antrag still acts as authoritative fallback
- Deterministic, reproducible behavior
"""

import os
from typing import Optional, Dict, Any
from fillpdf import fillpdfs


class UserProfile:
    """
    User profile data received from the frontend.
    
    PRIVACY CONSTRAINTS (STRICT):
    - This data is only used within the request scope
    - No data is persisted on the server
    - Bank data (BIC, IBAN, Kreditinstitut) is NEVER included in the profile
    """
    def __init__(self, data: Optional[Dict[str, Any]] = None):
        if data is None:
            data = {}
        # Use (value or '') to handle None values in the dict, then strip
        self.full_name: str = (data.get('full_name') or '').strip()
        self.phone_number: str = (data.get('phone_number') or '').strip()
        self.email: str = (data.get('email') or '').strip()
        self.postal_address: str = (data.get('postal_address') or '').strip()
        self.institute: str = (data.get('institute') or '').strip()
    
    def has_value(self, field: str) -> bool:
        """Check if a field has a non-empty value."""
        value = getattr(self, field, '')
        return bool(value and value.strip())
    
    def to_dict(self) -> Dict[str, str]:
        """Convert profile to dictionary."""
        return {
            'full_name': self.full_name,
            'phone_number': self.phone_number,
            'email': self.email,
            'postal_address': self.postal_address,
            'institute': self.institute,
        }


class antrag:
    def __init__(self, data_dir: str = ".", user_profile: Optional[Dict[str, Any]] = None):
        """
        Initialize antrag with a data directory for file operations.
        
        Args:
            data_dir: Directory where PDF files are located and output will be saved
            user_profile: Optional user profile data for prefilling. Format:
                {
                    'full_name': str,
                    'phone_number': str,
                    'email': str,
                    'postal_address': str,
                    'institute': str
                }
        """
        self.data_dir = data_dir
        self.user_profile = UserProfile(user_profile)
    
    def _get_prefilled_value(self, profile_value: str, antrag_value: Optional[str]) -> str:
        """
        Apply prefill priority logic.
        
        Priority:
        1. User profile value (if non-empty)
        2. Antrag extracted value (fallback)
        
        Args:
            profile_value: Value from user profile
            antrag_value: Value extracted from Antrag document
            
        Returns:
            The value to use (profile takes priority if non-empty)
        """
        # Profile value takes priority if it exists
        if profile_value and profile_value.strip():
            return profile_value.strip()
        # Fall back to Antrag value
        return antrag_value.strip() if antrag_value else ''
    
    def main(self, supervisor_name: str = None):
        """
        Main execution method for antrag processing.
        
        Implements prefill priority logic:
        1. Initialize form fields with user profile data
        2. Fill remaining empty fields from Antrag extraction
        3. Bank data ALWAYS comes from Antrag (never from profile for privacy)
        
        Args:
            supervisor_name: Optional supervisor name override. If None, uses value from form.
        """
        uploads_dir = os.path.join(os.path.dirname(__file__), "uploads")
        dienstreise_path = os.path.join(uploads_dir, "Dienstreiseantrag.pdf")
        templates_dir = os.path.join(os.path.dirname(__file__), "templates")
        reisekosten_path = os.path.join(templates_dir, "Reisekostenabrechnung_28_05_2024.pdf")
        filled_form_path = os.path.join(templates_dir, "filled_form.pdf")

        
        # Remove existing filled form if it exists
        if os.path.exists(filled_form_path):
            os.remove(filled_form_path)

        # Extract data from the Antrag PDF
        pdf_dict = fillpdfs.get_form_fields(dienstreise_path)
        
        # Apply prefill priority logic:
        # User profile values take priority, Antrag values fill in gaps
        
        # Name: Profile takes priority
        prefilled_name = self._get_prefilled_value(
            self.user_profile.full_name,
            pdf_dict.get("Name Vorname")
        )
        
        # Email: Profile takes priority
        prefilled_email = self._get_prefilled_value(
            self.user_profile.email,
            pdf_dict.get("EMa Adresse")
        )
        
        # Phone: Profile takes priority
        prefilled_phone = self._get_prefilled_value(
            self.user_profile.phone_number,
            pdf_dict.get("Telefon dienstlich")
        )
        
        # Address: Profile takes priority
        prefilled_address = self._get_prefilled_value(
            self.user_profile.postal_address,
            pdf_dict.get("Wohnort")
        )
        
        # Institute: Profile takes priority
        prefilled_institute = self._get_prefilled_value(
            self.user_profile.institute,
            pdf_dict.get("Institut")
        )
        
        # Bank data ALWAYS comes from Antrag (PRIVACY: never stored in profile)
        antrag_kreditinstitut = pdf_dict.get("Kreditinstitut")
        antrag_bic = pdf_dict.get("BIC")
        antrag_iban = pdf_dict.get("IBAN")
        
        # Safely get optional fields with empty string fallback to avoid TypeError
        kostenstelle = pdf_dict.get("Kostenstelle") or ""
        datum_6 = pdf_dict.get("Datum_6") or ""
        
        abrechnung_json = {
            "AntragstellerIn_Name_Vorname": prefilled_name,
            "E-Mail-dienstlich": prefilled_email,
            "Telefon_dienstlich": prefilled_phone,
            "\u00fe\u00ff\u0000P\u0000r\u0000i\u0000v\u0000a\u0000t\u0000e\u0000_\u0000A\u0000n\u0000s\u0000c\u0000h\u0000r\u0000i\u0000f\u0000t\u0000_\u0000S\u0000t\u0000r\u0000a\u0000\u00df\u0000e\u0000_\u0000P\u0000L\u0000Z\u0000_\u0000W\u0000o\u0000h\u0000n\u0000o\u0000r\u0000t": prefilled_address,
            "\u00fe\u00ff\u0000B\u0000e\u0000s\u0000c\u0000h\u0000\u00e4\u0000f\u0000t\u0000i\u0000g\u0000u\u0000n\u0000g\u0000s\u0000s\u0000t\u0000e\u0000l\u0000l\u0000e\u0000I\u0000n\u0000s\u0000t\u0000i\u0000t\u0000u\u0000t\u0000_\u0000e\u0000i\u0000n\u0000s\u0000c\u0000h\u0000l\u0000_\u0000A\u0000n\u0000s\u0000c\u0000h\u0000r\u0000i\u0000f\u0000t": prefilled_institute,
            "Kreditinstitut": antrag_kreditinstitut,
            "BIC": antrag_bic,
            "BAN": antrag_iban,
            "Tagegeld": "nein",
            "Drittmittelprojekt": "P" + kostenstelle,
            "Genehmigung_der_Dienstreise_am__von": datum_6 + " ",
        }

        # If supervisor_name is provided, override it
        if supervisor_name:
            current_value = abrechnung_json.get('Genehmigung_der_Dienstreise_am__von', '')
            abrechnung_json['Genehmigung_der_Dienstreise_am__von'] = current_value[:11] + supervisor_name

        try:
            print("Filling PDF form with merged profile + Antrag data...")
            fillpdfs.write_fillable_pdf(reisekosten_path, filled_form_path, abrechnung_json)
        except Exception as e:
            print(f"Error filling PDF form: {e}")
            raise
        finally:
            print("Antrag Process Complete")
