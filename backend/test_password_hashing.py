#!/usr/bin/env python3
"""
Manual test script for password hashing.
Run this to verify password hashing functionality.
"""
from app.core.security import hash_password, verify_password

def test_password_hashing():
    """Run comprehensive password hashing tests."""
    print("=" * 60)
    print("PASSWORD HASHING TESTS")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    # Test 1: Hash password
    print("\n[TEST 1] Hash password...")
    try:
        password = "TestPassword123"
        hashed = hash_password(password)
        assert hashed.startswith("$2b$")
        assert len(hashed) == 60
        print(f"   ✅ PASS - Hash: {hashed[:40]}...")
        passed += 1
    except AssertionError as e:
        print(f"   ❌ FAIL - {e}")
        failed += 1
    
    # Test 2: Verify correct password
    print("\n[TEST 2] Verify correct password...")
    try:
        password = "MySecurePassword123"
        hashed = hash_password(password)
        result = verify_password(password, hashed)
        assert result is True
        print("   ✅ PASS - Correct password verified")
        passed += 1
    except AssertionError:
        print("   ❌ FAIL - Correct password not verified")
        failed += 1
    
    # Test 3: Verify wrong password
    print("\n[TEST 3] Verify wrong password...")
    try:
        password = "CorrectPassword"
        hashed = hash_password(password)
        result = verify_password("WrongPassword", hashed)
        assert result is False
        print("   ✅ PASS - Wrong password rejected")
        passed += 1
    except AssertionError:
        print("   ❌ FAIL - Wrong password not rejected")
        failed += 1
    
    # Test 4: Same password different hashes
    print("\n[TEST 4] Same password produces different hashes...")
    try:
        password = "password123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        assert hash1 != hash2
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)
        print("   ✅ PASS - Different salt per hash")
        passed += 1
    except AssertionError:
        print("   ❌ FAIL - Hashes are same or don't verify")
        failed += 1
    
    # Test 5: Hash is irreversible
    print("\n[TEST 5] Hash is irreversible...")
    try:
        password = "SecretPassword"
        hashed = hash_password(password)
        assert password not in hashed
        print("   ✅ PASS - Original password not in hash")
        passed += 1
    except AssertionError:
        print("   ❌ FAIL - Password visible in hash")
        failed += 1
    
    # Test 6: Invalid hash returns False
    print("\n[TEST 6] Invalid hash returns False...")
    try:
        result = verify_password("password", "invalid_hash")
        assert result is False
        print("   ✅ PASS - Invalid hash handled gracefully")
        passed += 1
    except AssertionError:
        print("   ❌ FAIL - Invalid hash not handled")
        failed += 1
    
    # Test 7: Special characters
    print("\n[TEST 7] Special characters in password...")
    try:
        password = "P@ssw0rd!#$%^&*()"
        hashed = hash_password(password)
        assert verify_password(password, hashed)
        print("   ✅ PASS - Special characters work")
        passed += 1
    except AssertionError:
        print("   ❌ FAIL - Special characters failed")
        failed += 1
    
    # Test 8: Unicode characters
    print("\n[TEST 8] Unicode characters in password...")
    try:
        password = "Пароль123🔐"
        hashed = hash_password(password)
        assert verify_password(password, hashed)
        print("   ✅ PASS - Unicode characters work")
        passed += 1
    except AssertionError:
        print("   ❌ FAIL - Unicode characters failed")
        failed += 1
    
    # Test 9: Bcrypt rounds = 12
    print("\n[TEST 9] Bcrypt uses 12 rounds...")
    try:
        hashed = hash_password("test")
        cost_factor = hashed.split("$")[2]
        assert cost_factor == "12"
        print(f"   ✅ PASS - Using {cost_factor} rounds")
        passed += 1
    except AssertionError:
        print(f"   ❌ FAIL - Wrong cost factor: {cost_factor}")
        failed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print(f"RESULTS: {passed}/{passed+failed} tests passed")
    print("=" * 60)
    
    if failed == 0:
        print("✅ ALL TESTS PASSED!")
        return 0
    else:
        print(f"❌ {failed} TESTS FAILED")
        return 1

if __name__ == "__main__":
    exit(test_password_hashing())
