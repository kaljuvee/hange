#!/usr/bin/env python3
"""
Enhanced Document Extraction Tests
Tests the improved document processor with production features
"""

import os
import sys
import json
import pandas as pd
from datetime import datetime
from pathlib import Path

# Add parent directory to path to import modules
sys.path.append(str(Path(__file__).parent.parent))

from enhanced_document_processor import EnhancedDocumentProcessor, DocumentAnalysis, ExtractedField

def create_test_documents():
    """Create sample test documents for testing"""
    test_data_dir = Path(__file__).parent.parent / "test-data"
    test_data_dir.mkdir(exist_ok=True)
    
    # Sample DOCX content (simulated as text)
    docx_content = """
    RIIGIHANGE - IT TEENUSTE OSUTAMINE
    
    1. ÜLDANDMED
    Ettevõtte nimi: _______________
    Registrikood: _______________
    KMKR number: _______________
    
    2. KONTAKTANDMED
    Kontaktisik: _______________
    E-posti aadress: _______________
    Telefon: _______________
    Aadress: _______________
    
    3. PROJEKTI KIRJELDUS
    Projekti kirjeldus (min 500 tähemärki): _______________
    Kasutatavad tehnoloogiad: _______________
    Meeskonna suurus: _______________
    Projekti kestus (kuud): _______________
    
    4. FINANTSINFORMATSIOON
    Kogumaksumus (EUR): _______________
    Maksegraafik: [ ] Kuine [ ] Kvartaalne [ ] Etapipõhine
    
    5. KVALITEET JA VASTAVUS
    [ ] ISO 27001 sertifikaat
    [ ] GDPR vastavus
    [ ] Eesti keele tugi
    
    6. KOGEMUS
    Varasem kogemus (kirjeldage 3 sarnast projekti): _______________
    Sertifikaadid: _______________
    Soovitused: _______________
    
    NÕUDED:
    - Vähemalt 5 aastat kogemust avaliku sektori IT projektides
    - ISO 27001 sertifikaat kohustuslik
    - GDPR vastavuse tagamine
    - Eesti keele oskus
    - 24/7 tehnilise toe olemasolu
    """
    
    # Save test document
    with open(test_data_dir / "sample_it_procurement.txt", "w", encoding="utf-8") as f:
        f.write(docx_content)
    
    # Sample XLSX content (simulated as structured text)
    xlsx_content = """
    SHEET: Hinnapakkumise vorm
    
    HEADERS:
    Kirjeldus | Ühik | Kogus | Ühiku hind (EUR) | Kokku (EUR)
    
    DATA SAMPLE:
    Süsteemi analüüs | tund | 40 | 85.00 | 3400.00
    Arendus | tund | 200 | 75.00 | 15000.00
    Testimine | tund | 60 | 70.00 | 4200.00
    Dokumentatsioon | tund | 30 | 65.00 | 1950.00
    Koolitus | tund | 16 | 80.00 | 1280.00
    
    FORMULAS:
    FORMULA in E2: =C2*D2
    FORMULA in E7: =SUM(E2:E6)
    
    VALIDATION in D2: >0
    VALIDATION in C2: >0
    """
    
    with open(test_data_dir / "sample_pricing_form.txt", "w", encoding="utf-8") as f:
        f.write(xlsx_content)
    
    return test_data_dir

def test_document_processing():
    """Test the enhanced document processor"""
    print("🧪 Testing Enhanced Document Processor")
    print("=" * 50)
    
    # Initialize processor
    processor = EnhancedDocumentProcessor()
    
    # Create test documents
    test_data_dir = create_test_documents()
    
    # Test results
    results = []
    
    # Test 1: IT Procurement Document
    print("\n📄 Test 1: IT Procurement Document")
    print("-" * 30)
    
    try:
        doc_path = test_data_dir / "sample_it_procurement.txt"
        analysis = processor.process_document(str(doc_path), "text")
        
        print(f"✅ Document Type: {analysis.document_type}")
        print(f"✅ Title: {analysis.title}")
        print(f"✅ Confidence Score: {analysis.confidence_score:.2%}")
        print(f"✅ Processing Time: {analysis.processing_time:.2f}s")
        print(f"✅ Cache Hit: {analysis.cache_hit}")
        print(f"✅ Needs Review: {analysis.needs_human_review}")
        print(f"✅ Fields Extracted: {len(analysis.form_fields)}")
        print(f"✅ Requirements Found: {len(analysis.requirements)}")
        
        # Validate fields
        validation_errors = processor.validate_extracted_fields(analysis.form_fields)
        print(f"✅ Validation Errors: {len(validation_errors)}")
        
        # Test result
        test_result = {
            "test_name": "IT Procurement Document",
            "document_type": analysis.document_type,
            "confidence_score": analysis.confidence_score,
            "processing_time": analysis.processing_time,
            "fields_count": len(analysis.form_fields),
            "requirements_count": len(analysis.requirements),
            "validation_errors": len(validation_errors),
            "success": True,
            "cache_hit": analysis.cache_hit
        }
        
        # Show sample fields
        print("\n📋 Sample Extracted Fields:")
        for i, field in enumerate(analysis.form_fields[:5]):
            confidence_emoji = "🟢" if field.confidence_score > 0.8 else "🟡" if field.confidence_score > 0.5 else "🔴"
            print(f"  {confidence_emoji} {field.label} ({field.field_type}) - {field.confidence_score:.1%}")
        
        results.append(test_result)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        results.append({
            "test_name": "IT Procurement Document",
            "success": False,
            "error": str(e)
        })
    
    # Test 2: Pricing Form Document
    print("\n📊 Test 2: Pricing Form Document")
    print("-" * 30)
    
    try:
        doc_path = test_data_dir / "sample_pricing_form.txt"
        analysis = processor.process_document(str(doc_path), "xlsx")
        
        print(f"✅ Document Type: {analysis.document_type}")
        print(f"✅ Title: {analysis.title}")
        print(f"✅ Confidence Score: {analysis.confidence_score:.2%}")
        print(f"✅ Processing Time: {analysis.processing_time:.2f}s")
        print(f"✅ Cache Hit: {analysis.cache_hit}")
        print(f"✅ Fields Extracted: {len(analysis.form_fields)}")
        
        test_result = {
            "test_name": "Pricing Form Document",
            "document_type": analysis.document_type,
            "confidence_score": analysis.confidence_score,
            "processing_time": analysis.processing_time,
            "fields_count": len(analysis.form_fields),
            "success": True,
            "cache_hit": analysis.cache_hit
        }
        
        results.append(test_result)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        results.append({
            "test_name": "Pricing Form Document",
            "success": False,
            "error": str(e)
        })
    
    # Test 3: Cache Performance
    print("\n🚀 Test 3: Cache Performance")
    print("-" * 30)
    
    try:
        # Process the same document again to test caching
        doc_path = test_data_dir / "sample_it_procurement.txt"
        start_time = datetime.now()
        analysis = processor.process_document(str(doc_path), "text")
        cache_time = (datetime.now() - start_time).total_seconds()
        
        print(f"✅ Cache Hit: {analysis.cache_hit}")
        print(f"✅ Cache Processing Time: {cache_time:.3f}s")
        print(f"✅ Speed Improvement: {analysis.processing_time / cache_time:.1f}x faster" if analysis.cache_hit else "No cache hit")
        
        results.append({
            "test_name": "Cache Performance",
            "cache_hit": analysis.cache_hit,
            "cache_time": cache_time,
            "original_time": analysis.processing_time,
            "success": True
        })
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        results.append({
            "test_name": "Cache Performance",
            "success": False,
            "error": str(e)
        })
    
    # Test 4: Form Preview Generation
    print("\n🎨 Test 4: Form Preview Generation")
    print("-" * 30)
    
    try:
        doc_path = test_data_dir / "sample_it_procurement.txt"
        analysis = processor.process_document(str(doc_path), "text")
        
        # Generate form preview
        form_html = processor.generate_form_preview(analysis)
        
        print(f"✅ Form HTML Generated: {len(form_html)} characters")
        print(f"✅ Contains form elements: {'<form>' in form_html}")
        print(f"✅ Contains input fields: {'<input' in form_html}")
        print(f"✅ Contains confidence scores: {'confidence' in form_html}")
        
        # Save form preview
        preview_path = test_data_dir / "form_preview.html"
        with open(preview_path, "w", encoding="utf-8") as f:
            f.write(form_html)
        
        print(f"✅ Form preview saved to: {preview_path}")
        
        results.append({
            "test_name": "Form Preview Generation",
            "html_length": len(form_html),
            "has_form_elements": '<form>' in form_html,
            "success": True
        })
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        results.append({
            "test_name": "Form Preview Generation",
            "success": False,
            "error": str(e)
        })
    
    # Save test results
    results_file = test_data_dir / f"enhanced_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n💾 Test results saved to: {results_file}")
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 50)
    
    successful_tests = sum(1 for r in results if r.get('success', False))
    total_tests = len(results)
    
    print(f"✅ Successful Tests: {successful_tests}/{total_tests}")
    print(f"📈 Success Rate: {successful_tests/total_tests*100:.1f}%")
    
    # Performance summary
    processing_times = [r.get('processing_time', 0) for r in results if r.get('processing_time')]
    if processing_times:
        avg_time = sum(processing_times) / len(processing_times)
        print(f"⏱️  Average Processing Time: {avg_time:.2f}s")
    
    # Confidence summary
    confidence_scores = [r.get('confidence_score', 0) for r in results if r.get('confidence_score')]
    if confidence_scores:
        avg_confidence = sum(confidence_scores) / len(confidence_scores)
        print(f"🎯 Average Confidence Score: {avg_confidence:.1%}")
    
    return results

def test_with_sample_data():
    """Test with sample procurement data"""
    print("\n🗂️  Testing with Sample Procurement Data")
    print("=" * 50)
    
    # Load sample procurement data
    test_data_dir = Path(__file__).parent.parent / "test-data"
    sample_data_file = test_data_dir / "sample_procurement_data.json"
    
    if sample_data_file.exists():
        with open(sample_data_file, "r", encoding="utf-8") as f:
            sample_data = json.load(f)
        
        print(f"✅ Loaded {len(sample_data)} sample procurements")
        
        # Test data structure
        for i, procurement in enumerate(sample_data[:3]):
            print(f"\n📋 Procurement {i+1}: {procurement['title'][:50]}...")
            print(f"   Category: {procurement['category']}")
            print(f"   Value: €{procurement['estimated_value']:,}")
            print(f"   Documents: {len(procurement.get('documents', []))}")
        
        # Create CSV summary
        df = pd.DataFrame(sample_data)
        csv_file = test_data_dir / "procurement_summary.csv"
        df.to_csv(csv_file, index=False, encoding="utf-8")
        print(f"\n💾 Procurement summary saved to: {csv_file}")
        
        return True
    else:
        print("❌ Sample procurement data not found")
        return False

if __name__ == "__main__":
    print("🚀 Enhanced Document Extraction Testing")
    print("=" * 60)
    
    # Run tests
    test_results = test_document_processing()
    
    # Test with sample data
    test_with_sample_data()
    
    print("\n🎉 Testing completed!")
    print("Check the test-data/ directory for generated files and results.")

