"""
JWT Token Management Test Script

Tests token generation, validation, and expiration handling.
Run: python test_jwt.py
"""
import sys
import os
from datetime import timedelta
from time import sleep

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.core.security import create_access_token, decode_access_token
from fastapi import HTTPException


def test_token_generation():
    """Test 1: Generate token for test@example.com"""
    print("=" * 60)
    print("TEST 1: Token Generation")
    print("=" * 60)
    
    email = "test@example.com"
    token = create_access_token(email)
    
    print(f"✅ Generated token for: {email}")
    print(f"📝 Token: {token[:50]}...")
    print(f"📏 Token length: {len(token)} characters")
    print()
    
    return token


def test_token_decoding(token: str):
    """Test 2: Decode token and verify email"""
    print("=" * 60)
    print("TEST 2: Token Decoding")
    print("=" * 60)
    
    try:
        decoded_email = decode_access_token(token)
        print(f"✅ Token decoded successfully")
        print(f"📧 Extracted email: {decoded_email}")
        
        if decoded_email == "test@example.com":
            print("✅ Email matches original!")
        else:
            print(f"❌ Email mismatch! Expected: test@example.com, Got: {decoded_email}")
    except HTTPException as e:
        print(f"❌ Decoding failed: {e.detail}")
    
    print()


def test_invalid_token():
    """Test 3: Try to decode invalid token"""
    print("=" * 60)
    print("TEST 3: Invalid Token Handling")
    print("=" * 60)
    
    invalid_token = "invalid.token.here"
    
    try:
        decode_access_token(invalid_token)
        print("❌ Should have raised HTTPException!")
    except HTTPException as e:
        print(f"✅ Correctly rejected invalid token")
        print(f"📝 Status code: {e.status_code}")
        print(f"📝 Detail: {e.detail}")
    
    print()


def test_expired_token():
    """Test 4: Generate token with 1 second expiration and test after expiry"""
    print("=" * 60)
    print("TEST 4: Token Expiration")
    print("=" * 60)
    
    email = "expiry@test.com"
    
    # Create token that expires in 1 second
    short_lived_token = create_access_token(
        email,
        expires_delta=timedelta(seconds=1)
    )
    
    print(f"✅ Generated short-lived token (expires in 1 second)")
    
    # Test immediately - should work
    try:
        decoded = decode_access_token(short_lived_token)
        print(f"✅ Token valid immediately: {decoded}")
    except HTTPException:
        print("❌ Token should be valid immediately!")
    
    # Wait 2 seconds
    print("⏳ Waiting 2 seconds for token to expire...")
    sleep(2)
    
    # Test after expiration - should fail
    try:
        decode_access_token(short_lived_token)
        print("❌ Expired token should have been rejected!")
    except HTTPException as e:
        print(f"✅ Correctly rejected expired token")
        print(f"📝 Status code: {e.status_code}")
        print(f"📝 Detail: {e.detail}")
    
    print()


def test_token_payload_structure():
    """Test 5: Verify token payload structure"""
    print("=" * 60)
    print("TEST 5: Token Payload Structure")
    print("=" * 60)
    
    from jose import jwt
    from app.core.config import settings
    
    email = "payload@test.com"
    token = create_access_token(email)
    
    # Decode without verification to inspect payload
    payload = jwt.decode(
        token,
        settings.secret_key,
        algorithms=[settings.algorithm]
    )
    
    print("📦 Token Payload:")
    print(f"  - sub (subject): {payload.get('sub')}")
    print(f"  - exp (expiration): {payload.get('exp')}")
    print(f"  - iat (issued at): {payload.get('iat')}")
    
    required_fields = ['sub', 'exp', 'iat']
    missing = [f for f in required_fields if f not in payload]
    
    if not missing:
        print("✅ All required fields present")
    else:
        print(f"❌ Missing fields: {missing}")
    
    print()


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("JWT TOKEN MANAGEMENT TEST SUITE")
    print("=" * 60 + "\n")
    
    try:
        # Test 1: Generate token
        token = test_token_generation()
        
        # Test 2: Decode valid token
        test_token_decoding(token)
        
        # Test 3: Invalid token
        test_invalid_token()
        
        # Test 4: Expired token
        test_expired_token()
        
        # Test 5: Payload structure
        test_token_payload_structure()
        
        print("=" * 60)
        print("✅ ALL TESTS COMPLETED")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
