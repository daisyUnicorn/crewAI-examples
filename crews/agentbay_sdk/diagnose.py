#!/usr/bin/env python3
"""
Diagnostic script for AgentBay SDK + Bailian integration
Run this to check your configuration and connectivity
"""

import os
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

print("=" * 80)
print("🔍 AgentBay SDK Configuration Diagnostic")
print("=" * 80)

# Check 1: .env file exists
print("\n✓ Check 1: .env file")
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    print(f"  ✅ Found: {env_file}")
else:
    print(f"  ❌ NOT FOUND: {env_file}")
    print(f"  → Create .env file: cp env.example .env")
    sys.exit(1)

# Check 2: Load environment variables
print("\n✓ Check 2: Loading environment variables")
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("  ✅ python-dotenv loaded")
except ImportError:
    print("  ❌ python-dotenv not installed")
    print("  → Install: pip install python-dotenv")
    sys.exit(1)

# Check 3: Required variables
print("\n✓ Check 3: Required environment variables")
required_vars = {
    "AGENTBAY_API_KEY": "AgentBay SDK",
    "OPENAI_API_KEY": "LLM API",
}

optional_vars = {
    "OPENAI_API_BASE": "Custom API endpoint",
    "OPENAI_MODEL_NAME": "Model name",
}

all_ok = True
for var, desc in required_vars.items():
    value = os.getenv(var)
    if value:
        masked = value[:10] + "..." if len(value) > 10 else value
        print(f"  ✅ {var}: {masked} ({desc})")
    else:
        print(f"  ❌ {var}: NOT SET ({desc})")
        all_ok = False

for var, desc in optional_vars.items():
    value = os.getenv(var)
    if value:
        print(f"  ℹ️  {var}: {value} ({desc})")
    else:
        print(f"  ⚠️  {var}: NOT SET ({desc}) - using default")

if not all_ok:
    print("\n❌ Missing required variables. Please edit .env file.")
    sys.exit(1)

# Check 4: Network connectivity
print("\n✓ Check 4: Network connectivity")
api_base = os.getenv("OPENAI_API_BASE")
if api_base:
    print(f"  Testing: {api_base}")
    try:
        import urllib.request
        from urllib.error import HTTPError
        req = urllib.request.Request(api_base, method='HEAD')
        req.add_header('User-Agent', 'AgentBay-Diagnostic/1.0')
        try:
            with urllib.request.urlopen(req, timeout=5) as response:
                print(f"  ✅ Connection successful (HTTP {response.status})")
        except HTTPError as e:
            if e.code in [404, 401, 403]:
                print(f"  ✅ Server reachable (HTTP {e.code})")
                print(f"     This is normal - the endpoint exists and is accessible")
            else:
                print(f"  ⚠️  HTTP {e.code}: {e.reason}")
    except Exception as e:
        print(f"  ❌ Connection failed: {e}")
        print(f"     Check your network or firewall settings")
else:
    print("  ℹ️  Using default OpenAI endpoint")

# Check 5: Test OpenAI client
print("\n✓ Check 5: Testing LLM connection")
try:
    from openai import OpenAI

    client_kwargs = {"api_key": os.getenv("OPENAI_API_KEY")}
    if api_base:
        client_kwargs["base_url"] = api_base

    client = OpenAI(**client_kwargs)

    # Get model name
    model = os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")
    # Remove openai/ prefix if present (for direct API call)
    model_for_api = model.replace("openai/", "")

    print(f"  Testing with model: {model_for_api}")

    response = client.chat.completions.create(
        model=model_for_api,
        messages=[{"role": "user", "content": "Say 'OK' if you can read this"}],
        max_tokens=10
    )

    result = response.choices[0].message.content
    print(f"  ✅ LLM responded: {result}")

except Exception as e:
    print(f"  ❌ LLM connection failed: {e}")
    print(f"\n  Troubleshooting:")
    print(f"  - Check API key is valid")
    print(f"  - Verify API base URL (no trailing slash)")
    print(f"  - Ensure account has sufficient balance")
    print(f"  - For Bailian: model should be openai/qwen-plus")
    sys.exit(1)

# Check 6: Test AgentBay SDK
print("\n✓ Check 6: Testing AgentBay SDK")
try:
    from agentbay_sdk.api.wuying_agentbay_wrapper import AgentBayCodeExecutor

    executor = AgentBayCodeExecutor()
    print(f"  ✅ AgentBay SDK initialized")
    print(f"  Note: Actual code execution requires valid AGENTBAY_API_KEY")

except Exception as e:
    print(f"  ❌ AgentBay SDK error: {e}")
    print(f"  → Check wuying-agentbay-sdk is installed")
    sys.exit(1)

# Summary
print("\n" + "=" * 80)
print("✅ All checks passed!")
print("=" * 80)
print("\nYour configuration looks good. You can now run:")
print("  cd crews/agentbay_sdk")
print("  pytest src/agentbay_sdk/tests/test_agentbay_code_flow.py -v")
print()

