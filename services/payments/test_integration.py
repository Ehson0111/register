#!/usr/bin/env python3
"""
Test script for payments service integration with new bridge endpoints
"""
import os
import sys
import django

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.yookassa_integration.models import Invoice
from apps.yookassa_integration.invoice_sync_v2 import create_invoice_in_onec, register_payment_in_onec
from apps.yookassa_integration.onec_client_v2 import OneCClientV2

def test_bridge_connection():
    """Test basic bridge connection"""
    print("=== Test Bridge Connection ===")
    try:
        client = OneCClientV2()
        # This will test basic bridge connectivity
        print(f"Bridge URL: {client.base_url}")
        print("Bridge client initialized successfully")
        return True
    except Exception as e:
        print(f"Bridge connection failed: {e}")
        return False

def test_invoice_creation():
    """Test invoice creation through new bridge"""
    print("\n=== Test Invoice Creation ===")
    try:
        # Create a test invoice
        invoice = Invoice.objects.create(
            invoice_number="TEST-001",
            deal_id="test-deal-001",
            contact_id="test-contact-001",
            service_id="test-service-001",
            amount=15000.00,
            comment="Test invoice for bridge integration"
        )
        
        print(f"Created test invoice: {invoice.invoice_number}")
        
        # Test creating invoice in 1C
        result = create_invoice_in_onec(invoice)
        print(f"Invoice created in 1C: {result.onec_document_id}")
        print(f"1C invoice number: {result.onec_invoice_number}")
        return True
    except Exception as e:
        print(f"Invoice creation failed: {e}")
        return False

def test_payment_registration():
    """Test payment registration through new bridge"""
    print("\n=== Test Payment Registration ===")
    try:
        # Find a test invoice
        invoice = Invoice.objects.filter(
            invoice_number="TEST-001"
        ).first()
        
        if not invoice:
            print("No test invoice found")
            return False
            
        if not invoice.onec_document_id:
            print("Invoice not synced with 1C")
            return False
        
        # Test payment registration
        payment_payload = {
            "id": "test-payment-001",
            "status": "succeeded",
            "amount": {"value": "15000.00", "currency": "RUB"},
            "captured_at": "2026-04-23T00:00:00",
            "payment_method": {"type": "yookassa"},
        }
        
        result = register_payment_in_onec(invoice, payment_payload)
        print(f"Payment registered in 1C: {result.onec_payment_document_id}")
        print(f"Invoice status: {result.status}")
        return True
    except Exception as e:
        print(f"Payment registration failed: {e}")
        return False

def main():
    print("Starting payments service integration tests...")
    
    tests = [
        ("Bridge Connection", test_bridge_connection),
        ("Invoice Creation", test_invoice_creation),
        ("Payment Registration", test_payment_registration),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        try:
            result = test_func()
            results.append((test_name, result))
            print(f"Result: {'PASS' if result else 'FAIL'}")
        except Exception as e:
            print(f"Error in {test_name}: {e}")
            results.append((test_name, False))
    
    print(f"\n{'='*50}")
    print("TEST RESULTS:")
    for test_name, result in results:
        print(f"{'PASS' if result else 'FAIL'} {test_name}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"\nPassed: {passed}/{total} tests")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
