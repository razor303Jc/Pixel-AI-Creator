#!/usr/bin/env python3
"""
Simple Environment Test
"""

import os
from pathlib import Path
from dotenv import load_dotenv


def test_env_loading():
    """Test environment variable loading"""
    print("🔍 Testing Environment Variable Loading")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Script location: {Path(__file__).parent}")

    # Check if .env exists
    env_file = Path(__file__).parent / ".env"
    print(f".env file path: {env_file}")
    print(f".env file exists: {env_file.exists()}")

    if env_file.exists():
        print(f".env file size: {env_file.stat().st_size} bytes")
        with open(env_file, "r") as f:
            content = f.read()
            print(f"First 200 chars of .env:\n{content[:200]}")

    # Try loading .env
    print("\n🔄 Loading .env file...")
    load_result = load_dotenv(env_file)
    print(f"load_dotenv result: {load_result}")

    # Check specific variables
    test_vars = ["DATABASE_URL", "SECRET_KEY", "OPENAI_API_KEY"]
    print(f"\n🔍 Checking environment variables:")
    for var in test_vars:
        value = os.getenv(var)
        if value:
            print(
                f"✅ {var}: {value[:20]}..."
                if len(value) > 20
                else f"✅ {var}: {value}"
            )
        else:
            print(f"❌ {var}: NOT SET")


if __name__ == "__main__":
    test_env_loading()
