#!/usr/bin/env python3

import json
import sys
from pathlib import Path

# Import the conversion function
from fhir2medkit import documentreference_to_medkit

def main():
    # Load the example FHIR DocumentReference JSON
    example_path = Path("example/document_reference.json")
    
    if not example_path.exists():
        print(f"Error: {example_path} not found!")
        sys.exit(1)
    
    print("Loading FHIR DocumentReference from example/document_reference.json...")
    with open(example_path, 'r') as f:
        dr_json = json.load(f)
    
    print(f"Resource Type: {dr_json['resourceType']}")
    print(f"ID: {dr_json['id']}")
    print(f"Subject: {dr_json['subject']['display']}")
    print(f"Date: {dr_json['date']}")
    print(f"Content Type: {dr_json['content'][0]['attachment']['contentType']}")
    print()
    
    try:
        # Convert FHIR DocumentReference to MedKit document
        print("Converting FHIR DocumentReference to MedKit document...")
        medkit_doc = documentreference_to_medkit(dr_json)
        
        print("✅ Conversion successful!")
        print(f"MedKit Document Type: {type(medkit_doc).__name__}")
        print(f"Text Length: {len(medkit_doc.text)} characters")
        print(f"Metadata keys: {list(medkit_doc.metadata.keys())}")
        print()
        
        # Display extracted text (first 200 characters)
        print("Extracted Text (first 200 chars):")
        print("-" * 50)
        print(medkit_doc.text[:200] + "..." if len(medkit_doc.text) > 200 else medkit_doc.text)
        print("-" * 50)
        print()
        
        # Display some metadata
        print("Selected Metadata:")
        metadata_to_show = ['fhir_id', 'fhir_subject', 'fhir_type', 'fhir_date', 
                          'fhir_contentType', 'fhir_size']
        for key in metadata_to_show:
            if key in medkit_doc.metadata:
                print(f"  {key}: {medkit_doc.metadata[key]}")
        
        print("\n🎉 Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during conversion: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()