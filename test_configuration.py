#!/usr/bin/env python3
"""
Test script to verify the new configuration system works
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from models.request_models import ReadmeRequest, CustomCredentials
from app import ReadmeGeneratorApp

def test_hosted_service():
    """Test with hosted service (default)"""
    print("🔧 Testing hosted service configuration...")
    
    request = ReadmeRequest(
        repo_url="https://github.com/test/repo.git",
        model_name="gpt-4o",
        provider="azure_openai",
        use_hosted_service=True
    )
    
    try:
        app = ReadmeGeneratorApp(request)
        print("✅ Hosted service configuration works!")
        return True
    except Exception as e:
        print(f"❌ Hosted service failed: {e}")
        return False

def test_custom_credentials():
    """Test with custom credentials"""
    print("\n🔧 Testing custom credentials configuration...")
    
    custom_creds = CustomCredentials(
        azure_api_key="test_key",
        azure_endpoint="https://test.openai.azure.com/",
        azure_api_version="2024-12-01-preview",
        azure_deployment="gpt-4o"
    )
    
    request = ReadmeRequest(
        repo_url="https://github.com/test/repo.git",
        model_name="gpt-4o",
        provider="azure_openai",
        use_hosted_service=False,
        custom_credentials=custom_creds
    )
    
    try:
        app = ReadmeGeneratorApp(request)
        print("✅ Custom credentials configuration works!")
        return True
    except Exception as e:
        print(f"❌ Custom credentials failed: {e}")
        return False

def test_validation():
    """Test validation logic"""
    print("\n🔧 Testing validation logic...")
    
    # Test invalid custom credentials (missing required fields)
    request = ReadmeRequest(
        repo_url="https://github.com/test/repo.git",
        model_name="gpt-4o",
        provider="azure_openai",
        use_hosted_service=False,
        custom_credentials=CustomCredentials(azure_api_key="test_key")  # Missing endpoint and deployment
    )
    
    try:
        app = ReadmeGeneratorApp(request)
        print("❌ Validation failed - should have rejected incomplete credentials")
        return False
    except Exception as e:
        print(f"✅ Validation works - correctly rejected incomplete credentials: {e}")
        return True

if __name__ == "__main__":
    print("🚀 Testing GitRot Configuration System\n")
    
    results = []
    results.append(test_hosted_service())
    results.append(test_custom_credentials())
    results.append(test_validation())
    
    print(f"\n📊 Results: {sum(results)}/{len(results)} tests passed")
    
    if all(results):
        print("🎉 All tests passed! Configuration system is ready!")
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        sys.exit(1)