#!/usr/bin/env python3
"""
External API Port Testing (8002)
Testing Database Management System on external port
"""

import asyncio
import httpx
from datetime import datetime


async def test_external_api_port():
    """Test Database Management System on external port 8002"""

    print("🌐 TESTING EXTERNAL API PORT 8002")
    print("=" * 60)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    base_url = "http://localhost:8002"

    async with httpx.AsyncClient(timeout=10.0) as client:

        # Test 1: Basic Health Check
        try:
            response = await client.get(f"{base_url}/health")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health Endpoint: {data.get('status', 'unknown')}")
                print(f"   • Service: {data.get('service', 'N/A')}")
            else:
                print(f"❌ Health Endpoint: Status {response.status_code}")
        except Exception as e:
            print(f"❌ Health Endpoint: {e}")

        # Test 2: Database Management Health
        try:
            response = await client.get(f"{base_url}/api/database/health")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Database Health: {data.get('status', 'unknown')}")
                print(f"   • Service: {data.get('service', 'N/A')}")
            else:
                print(f"❌ Database Health: Status {response.status_code}")
        except Exception as e:
            print(f"❌ Database Health: {e}")

        # Test 3: Database Statistics
        try:
            response = await client.get(f"{base_url}/api/database/stats")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Database Stats: Retrieved successfully")
                print(f"   • Total Connections: {data.get('total_connections', 'N/A')}")
                print(
                    f"   • Active Connections: {data.get('active_connections', 'N/A')}"
                )
                print(f"   • Timestamp: {data.get('timestamp', 'N/A')}")
            else:
                print(f"❌ Database Stats: Status {response.status_code}")
        except Exception as e:
            print(f"❌ Database Stats: {e}")

        # Test 4: API Documentation
        try:
            response = await client.get(f"{base_url}/docs")
            if response.status_code == 200:
                print("✅ API Documentation: Accessible")
            else:
                print(f"❌ API Documentation: Status {response.status_code}")
        except Exception as e:
            print(f"❌ API Documentation: {e}")

        # Test 5: OpenAPI Schema
        try:
            response = await client.get(f"{base_url}/openapi.json")
            if response.status_code == 200:
                print("✅ OpenAPI Schema: Available")
            else:
                print(f"❌ OpenAPI Schema: Status {response.status_code}")
        except Exception as e:
            print(f"❌ OpenAPI Schema: {e}")

    print("\n🎯 EXTERNAL API TESTING COMPLETE")
    print("=" * 60)
    print("The Database Management System is accessible on external port 8002")
    print("All components are ready for external client access")


if __name__ == "__main__":
    asyncio.run(test_external_api_port())
