/**
 * Verification utilities for validating AI-extracted travel data.
 */

export interface VerifiableField {
  key: string;
  label: string;
  category: 'date' | 'time' | 'location';
  placeholder: string;
  extractedValue: string;
  verifiedValue: string;
  isVerified: boolean;
}

export interface VerificationData {
  hinreise: VerifiableField[];
  ruckreise: VerifiableField[];
  hotel: VerifiableField[];
}

// Define which fields are verifiable for each section
// These keys must match what the backend Python modules return

export const HINREISE_VERIFIABLE_FIELDS: Array<{
  key: string;
  label: string;
  category: 'date' | 'time' | 'location';
  placeholder: string;
}> = [
  {
    key: 'Hinreise_Beginn',
    label: 'Departure Date',
    category: 'date',
    placeholder: 'DD.MM.YYYY',
  },
  {
    key: 'Hinreise_Uhrzeit',
    label: 'Departure Time',
    category: 'time',
    placeholder: 'HH:MM',
  },
  {
    key: 'Hinreise_von',
    label: 'Departure From',
    category: 'location',
    placeholder: 'City/Airport',
  },
  {
    key: 'Hinreise_nach',
    label: 'Arrival At',
    category: 'location',
    placeholder: 'City/Airport',
  },
  {
    key: 'Hinreise_Ort',
    label: 'Departure Location Type',
    category: 'location',
    placeholder: 'Wohnung/Dienststelle',
  },
];

export const RUCKREISE_VERIFIABLE_FIELDS: Array<{
  key: string;
  label: string;
  category: 'date' | 'time' | 'location';
  placeholder: string;
}> = [
  {
    key: 'þÿ\u0000R\u0000ü\u0000c\u0000k\u0000r\u0000e\u0000i\u0000s\u0000e\u0000 \u0000a\u0000m',
    label: 'Return Date',
    category: 'date',
    placeholder: 'DD.MM.YYYY',
  },
  {
    key: 'þÿ\u0000R\u0000ü\u0000c\u0000k\u0000r\u0000e\u0000i\u0000s\u0000e\u0000 \u0000U\u0000h\u0000r\u0000z\u0000e\u0000i\u0000t',
    label: 'Return Time',
    category: 'time',
    placeholder: 'HH:MM',
  },
  {
    key: 'þÿ\u0000R\u0000ü\u0000c\u0000k\u0000r\u0000e\u0000i\u0000s\u0000e\u0000 \u0000v\u0000o\u0000n',
    label: 'Return From',
    category: 'location',
    placeholder: 'City/Airport',
  },
  {
    key: 'þÿ\u0000R\u0000ü\u0000c\u0000k\u0000r\u0000e\u0000i\u0000s\u0000e\u0000 \u0000n\u0000a\u0000c\u0000h',
    label: 'Return To',
    category: 'location',
    placeholder: 'City/Airport',
  },
  {
    key: 'þÿ\u0000R\u0000ü\u0000c\u0000k\u0000r\u0000e\u0000i\u0000s\u0000e\u0000 \u0000E\u0000n\u0000d\u0000e\u0000 \u0000a\u0000m',
    label: 'Home Arrival Date',
    category: 'date',
    placeholder: 'DD.MM.YYYY',
  },
  {
    key: 'þÿ\u0000R\u0000ü\u0000c\u0000k\u0000r\u0000e\u0000i\u0000s\u0000e\u0000 \u0000E\u0000n\u0000d\u0000e\u0000 \u0000U\u0000h\u0000r\u0000z\u0000e\u0000i\u0000t',
    label: 'Home Arrival Time',
    category: 'time',
    placeholder: 'HH:MM',
  },
  {
    key: 'Rückreise_Ort',
    label: 'Arrival Location Type',
    category: 'location',
    placeholder: 'Wohnung/Dienststelle',
  },
];

export const HOTEL_VERIFIABLE_FIELDS: Array<{
  key: string;
  label: string;
  category: 'date' | 'time' | 'location';
  placeholder: string;
}> = [
  {
    key: '\u00fe\u00ff\u0000G\u0000e\u0000s\u0000c\u0000h\u0000\u00e4\u0000f\u0000t\u0000s\u0000o\u0000r\u0000t\u0000_\u0000a\u0000m',
    label: 'Hotel Arrival Date',
    category: 'date',
    placeholder: 'DD.MM.YYYY',
  },
  {
    key: '\u00fe\u00ff\u0000G\u0000e\u0000s\u0000c\u0000h\u0000\u00e4\u0000f\u0000t\u0000s\u0000o\u0000r\u0000t\u0000_\u0000U\u0000h\u0000r\u0000z\u0000e\u0000i\u0000t',
    label: 'Hotel Check-in Time',
    category: 'time',
    placeholder: 'HH:MM',
  },
  {
    key: '\u00fe\u00ff\u0000D\u0000i\u0000e\u0000n\u0000s\u0000t\u0000g\u0000e\u0000s\u0000c\u0000h\u0000\u00e4\u0000f\u0000t\u0000_\u0000a\u0000m',
    label: 'Conference Start Date',
    category: 'date',
    placeholder: 'DD.MM.YYYY',
  },
  {
    key: '\u00fe\u00ff\u0000D\u0000i\u0000e\u0000n\u0000s\u0000t\u0000g\u0000e\u0000s\u0000c\u0000h\u0000\u00e4\u0000f\u0000t\u0000_\u0000u\u0000m',
    label: 'Conference Start Time',
    category: 'time',
    placeholder: 'HH:MM',
  },
  {
    key: '\u00fe\u00ff\u0000E\u0000n\u0000d\u0000e\u0000_\u0000D\u0000i\u0000e\u0000n\u0000s\u0000t\u0000g\u0000e\u0000s\u0000c\u0000h\u0000\u00e4\u0000f\u0000t\u0000_\u0000a\u0000m',
    label: 'Conference End Date',
    category: 'date',
    placeholder: 'DD.MM.YYYY',
  },
  {
    key: '\u00fe\u00ff\u0000E\u0000n\u0000d\u0000e\u0000_\u0000D\u0000i\u0000e\u0000n\u0000s\u0000t\u0000g\u0000e\u0000s\u0000c\u0000h\u0000\u00e4\u0000f\u0000t\u0000_\u0000u\u0000m',
    label: 'Conference End Time',
    category: 'time',
    placeholder: 'HH:MM',
  },
];


/**
 * Initialize verification data from extracted data.
 */
export function initializeVerificationData(extractedData: {
  hinreise: Record<string, string>;
  ruckreise: Record<string, string>;
  hotel: Record<string, string>;
}): VerificationData {
  const createFields = (
    fieldDefs: typeof HINREISE_VERIFIABLE_FIELDS,
    data: Record<string, string>
  ): VerifiableField[] => {
    return fieldDefs.map(def => ({
      key: def.key,
      label: def.label,
      category: def.category,
      placeholder: def.placeholder,
      extractedValue: data[def.key] || '',
      verifiedValue: data[def.key] || '',
      isVerified: false,
    }));
  };

  return {
    hinreise: createFields(HINREISE_VERIFIABLE_FIELDS, extractedData.hinreise),
    ruckreise: createFields(RUCKREISE_VERIFIABLE_FIELDS, extractedData.ruckreise),
    hotel: createFields(HOTEL_VERIFIABLE_FIELDS, extractedData.hotel),
  };
}

/**
 * Validate a single field.
 * Returns an error message if invalid, null if valid.
 */
export function validateField(field: VerifiableField): string | null {
  const value = field.verifiedValue.trim();
  
  // Empty is allowed (optional fields)
  if (!value) return null;
  
  switch (field.category) {
    case 'date':
      // Expect DD.MM.YYYY format
      if (!/^\d{2}\.\d{2}\.\d{4}$/.test(value)) {
        return 'Use format DD.MM.YYYY';
      }
      break;
    case 'time':
      // Expect HH:MM format
      if (!/^\d{2}:\d{2}$/.test(value)) {
        return 'Use format HH:MM';
      }
      break;
    case 'location':
      // Just check it's not too short
      if (value.length < 2) {
        return 'Please enter a valid location';
      }
      break;
  }
  
  return null;
}

/**
 * Check if all fields are valid.
 */
export function areAllFieldsValid(fields: VerifiableField[]): boolean {
  return fields.every(field => validateField(field) === null);
}

/**
 * Convert verification data back to backend format.
 */
export function toBackendFormat(data: VerificationData): {
  hinreise: Record<string, string>;
  ruckreise: Record<string, string>;
  hotel: Record<string, string>;
} {
  const toRecord = (fields: VerifiableField[]): Record<string, string> => {
    const result: Record<string, string> = {};
    for (const field of fields) {
      result[field.key] = field.verifiedValue;
    }
    return result;
  };

  return {
    hinreise: toRecord(data.hinreise),
    ruckreise: toRecord(data.ruckreise),
    hotel: toRecord(data.hotel),
  };
}
