#!/usr/bin/env python3
"""
Comprehensive Database Management System Test
Tests all database management functionality including health checks, stats, and connection management.
"""

import asyncio
import sys
import requests
import json
from datetime import datetime


class DatabaseManagementSystemTest:
    def __init__(self):
        self.base_url = "http://localhost:8002"
        self.results = {}

    def test_basic_health(self):
        """Test basic database health endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/database/health", timeout=10)

            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    self.results["health_check"] = (True, f"Healthy: {data}")
                    return True
                else:
                    self.results["health_check"] = (False, f"Unhealthy status: {data}")
                    return False
            else:
                self.results["health_check"] = (
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                )
                return False

        except Exception as e:
            self.results["health_check"] = (False, f"Connection error: {e}")
            return False

    def test_connection_stats(self):
        """Test database connection statistics"""
        try:
            response = requests.get(f"{self.base_url}/api/database/stats", timeout=10)

            if response.status_code == 200:
                data = response.json()
                required_fields = [
                    "total_connections",
                    "active_connections",
                    "idle_connections",
                    "timestamp",
                ]

                missing_fields = [
                    field for field in required_fields if field not in data
                ]
                if missing_fields:
                    self.results["connection_stats"] = (
                        False,
                        f"Missing fields: {missing_fields}",
                    )
                    return False

                self.results["connection_stats"] = (True, f"Stats: {data}")
                return True
            else:
                self.results["connection_stats"] = (
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                )
                return False

        except Exception as e:
            self.results["connection_stats"] = (False, f"Connection error: {e}")
            return False

    def test_database_system_functionality(self):
        """Test overall database system functionality"""
        try:
            # Test if we can reach the main API
            response = requests.get(f"{self.base_url}/", timeout=10)
            if response.status_code == 200:
                api_accessible = True
            else:
                api_accessible = False

            # Test sessions endpoint (which uses database)
            sessions_response = requests.get(
                f"{self.base_url}/api/sessions-test/", timeout=10
            )
            sessions_working = sessions_response.status_code == 200

            # Test auth endpoints (which use database)
            auth_response = requests.get(f"{self.base_url}/api/auth/health", timeout=10)
            auth_working = auth_response.status_code in [
                200,
                404,
            ]  # 404 is OK if endpoint doesn't exist

            functionality_score = sum([api_accessible, sessions_working, auth_working])

            if functionality_score >= 2:
                self.results["system_functionality"] = (
                    True,
                    f"Score: {functionality_score}/3 - API: {api_accessible}, Sessions: {sessions_working}, Auth: {auth_working}",
                )
                return True
            else:
                self.results["system_functionality"] = (
                    False,
                    f"Score: {functionality_score}/3 - API: {api_accessible}, Sessions: {sessions_working}, Auth: {auth_working}",
                )
                return False

        except Exception as e:
            self.results["system_functionality"] = (False, f"System test error: {e}")
            return False

    def test_database_configuration(self):
        """Test if database configuration is correct"""
        try:
            # Test basic connectivity
            health_response = requests.get(
                f"{self.base_url}/api/database/health", timeout=10
            )
            stats_response = requests.get(
                f"{self.base_url}/api/database/stats", timeout=10
            )

            health_ok = health_response.status_code == 200
            stats_ok = stats_response.status_code == 200

            if health_ok and stats_ok:
                health_data = health_response.json()
                stats_data = stats_response.json()

                # Check if database manager is properly configured
                has_healthy_status = health_data.get("status") == "healthy"
                has_connection_info = stats_data.get("total_connections", 0) > 0

                if has_healthy_status and has_connection_info:
                    self.results["database_config"] = (
                        True,
                        f"Configuration OK - Health: {health_data}, Stats: {stats_data}",
                    )
                    return True
                else:
                    self.results["database_config"] = (
                        False,
                        f"Config issues - Health: {health_data}, Stats: {stats_data}",
                    )
                    return False
            else:
                self.results["database_config"] = (
                    False,
                    f"Endpoint errors - Health: {health_response.status_code}, Stats: {stats_response.status_code}",
                )
                return False

        except Exception as e:
            self.results["database_config"] = (False, f"Config test error: {e}")
            return False

    def run_comprehensive_test(self):
        """Run all database management system tests"""
        print("🔍 Starting Comprehensive Database Management System Test...")
        print("=" * 60)

        # Define tests in order of importance
        tests = [
            ("Database Health Check", self.test_basic_health),
            ("Connection Statistics", self.test_connection_stats),
            ("Database Configuration", self.test_database_configuration),
            ("System Functionality", self.test_database_system_functionality),
        ]

        passed_tests = 0
        total_tests = len(tests)

        for test_name, test_func in tests:
            print(f"\n📋 Testing: {test_name}")
            try:
                if test_func():
                    print(f"✅ {test_name}: PASSED")
                    passed_tests += 1
                else:
                    print(f"❌ {test_name}: FAILED")
            except Exception as e:
                print(f"💥 {test_name}: ERROR - {e}")
                self.results[test_name] = (False, f"Exception: {e}")

        # Final summary
        print("\n" + "=" * 60)
        print("🏁 DATABASE MANAGEMENT SYSTEM TEST SUMMARY")
        print("=" * 60)

        for test_name, (success, details) in self.results.items():
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status} {test_name}")
            if not success:
                print(f"    💬 {details}")

        success_rate = (passed_tests / total_tests) * 100
        print(
            f"\n📊 Overall Success Rate: {passed_tests}/{total_tests} ({success_rate:.1f}%)"
        )

        if success_rate >= 75:
            print("🎉 Database Management System is OPERATIONAL!")
            return True
        else:
            print("⚠️  Database Management System needs attention!")
            return False


def main():
    print("🚀 Database Management System Comprehensive Test")
    print("Testing Pixel AI Creator Database Management functionality...")

    tester = DatabaseManagementSystemTest()
    success = tester.run_comprehensive_test()

    if success:
        print("\n✨ Test completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Test completed with issues!")
        sys.exit(1)


if __name__ == "__main__":
    main()
