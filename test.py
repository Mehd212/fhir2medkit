#!/usr/bin/env python3

import json
import sys
from pathlib import Path

# Import the conversion function
from fhir2medkit import documentreference_to_medkit

def test_document(file_path, description):
    """Test conversion of a single document"""
    print(f"\n{'='*60}")
    print(f"Testing: {description}")
    print('='*60)
    
    if not file_path.exists():
        print(f"Error: {file_path} not found!")
        return False
    
    print(f"Loading FHIR DocumentReference from {file_path}...")
    with open(file_path, 'r') as f:
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
        
        # Display extracted text (first 300 characters)
        print("Extracted Text (first 300 chars):")
        print("-" * 50)
        print(medkit_doc.text[:300] + "..." if len(medkit_doc.text) > 300 else medkit_doc.text)
        print("-" * 50)
        print()
        
        # Display some metadata
        print("Selected Metadata:")
        metadata_to_show = ['fhir_id', 'fhir_subject', 'fhir_type', 'fhir_date', 
                          'fhir_contentType', 'fhir_size', 'extracted_from_pdf']
        for key in metadata_to_show:
            if key in medkit_doc.metadata:
                print(f"  {key}: {medkit_doc.metadata[key]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during conversion: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🧪 FHIR to MedKit Conversion Test Suite")
    print("Testing multiple document types...")
    
    test_cases = [
        (Path("example/document_reference.json"), "Text Document (Medical Report)"),
        (Path("example/lab_report_reference.json"), "PDF Document (Laboratory Report)")
    ]
    
    results = []
    for file_path, description in test_cases:
        success = test_document(file_path, description)
        results.append((description, success))
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print('='*60)
    
    all_passed = True
    for description, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status}: {description}")
        if not success:
            all_passed = False
    
    if all_passed:
        print(f"\n🎉 All tests completed successfully!")
        sys.exit(0)
    else:
        print(f"\n💥 Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()