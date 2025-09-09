#!/usr/bin/env python3
"""
Comprehensive test suite for the Multi-Agent AI System
Tests all major functionality and validates the system is working correctly
"""
import json
import time
import sys
from typing import Any

import pytest

try:
    import requests
except ModuleNotFoundError:  # pragma: no cover - dependency missing
    pytest.skip("requests not installed", allow_module_level=True)

# Test configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"


class SystemTester:
    """Comprehensive system tester"""

    def __init__(self):
        self.test_results = []
        self.project_uuid = None

    def log_test(
        self, test_name: str, success: bool, message: str = "", data: Any = None
    ):
        """Log test result"""
        status = "PASS" if success else "FAIL"
        print(f"[{status}] {test_name}: {message}")

        self.test_results.append(
            {"test": test_name, "success": success, "message": message, "data": data}
        )

    def test_health_check(self):
        """Test system health endpoint"""
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    self.log_test("Health Check", True, "System is healthy", data)
                    return True
                else:
                    self.log_test(
                        "Health Check",
                        False,
                        f"Unexpected status: {data.get('status')}",
                    )
                    return False
            else:
                self.log_test("Health Check", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Health Check", False, f"Exception: {e}")
            return False

    def test_system_status(self):
        """Test system status endpoint"""
        try:
            response = requests.get(f"{BASE_URL}/status", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test("System Status", True, "System status retrieved", data)
                return True
            else:
                self.log_test("System Status", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("System Status", False, f"Exception: {e}")
            return False

    def test_project_creation(self):
        """Test project creation"""
        try:
            project_data = {
                "name": "Test E-commerce Website",
                "description": "A comprehensive e-commerce website with user authentication, product catalog, shopping cart, and payment processing",
                "project_type": "web_application",
                "requirements": "User registration and authentication, Product catalog with search and filtering, Shopping cart functionality, Payment processing integration, Responsive design for mobile and desktop, Admin panel for product management, Order tracking system, Email notifications",
            }

            response = requests.post(
                f"{API_BASE}/projects/",
                json=project_data,
                headers={"Content-Type": "application/json"},
                timeout=30,
            )

            if response.status_code == 200:
                data = response.json()
                self.project_uuid = data.get("project_uuid")
                if self.project_uuid:
                    self.log_test(
                        "Project Creation",
                        True,
                        f"Project created: {self.project_uuid}",
                        data,
                    )
                    return True
                else:
                    self.log_test("Project Creation", False, "No project UUID returned")
                    return False
            else:
                self.log_test(
                    "Project Creation",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                )
                return False
        except Exception as e:
            self.log_test("Project Creation", False, f"Exception: {e}")
            return False

    def test_project_processing(self):
        """Test project processing by monitoring status"""
        if not self.project_uuid:
            self.log_test("Project Processing", False, "No project UUID available")
            return False

        try:
            # Monitor project status for up to 60 seconds
            start_time = time.time()
            max_wait = 60

            while time.time() - start_time < max_wait:
                response = requests.get(
                    f"{API_BASE}/projects/{self.project_uuid}/status", timeout=10
                )

                if response.status_code == 200:
                    data = response.json()
                    status = data.get("status")
                    progress = data.get("progress", 0)
                    current_phase = data.get("current_phase")

                    print(
                        f"  Status: {status}, Progress: {progress:.1f}%, Phase: {current_phase}"
                    )

                    if status == "completed":
                        self.log_test(
                            "Project Processing",
                            True,
                            f"Project completed in {time.time() - start_time:.1f}s",
                            data,
                        )
                        return True
                    elif status == "failed":
                        self.log_test(
                            "Project Processing",
                            False,
                            f"Project failed: {data.get('error_message')}",
                        )
                        return False

                    # Wait before next check
                    time.sleep(2)
                else:
                    self.log_test(
                        "Project Processing", False, f"HTTP {response.status_code}"
                    )
                    return False

            # Timeout
            self.log_test("Project Processing", False, f"Timeout after {max_wait}s")
            return False

        except Exception as e:
            self.log_test("Project Processing", False, f"Exception: {e}")
            return False

    def test_project_results(self):
        """Test retrieving project results"""
        if not self.project_uuid:
            self.log_test("Project Results", False, "No project UUID available")
            return False

        try:
            response = requests.get(
                f"{API_BASE}/projects/{self.project_uuid}/results", timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Project Results", True, "Results retrieved successfully", data
                )
                return True
            else:
                self.log_test(
                    "Project Results",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                )
                return False
        except Exception as e:
            self.log_test("Project Results", False, f"Exception: {e}")
            return False

    def test_project_listing(self):
        """Test project listing"""
        try:
            response = requests.get(f"{API_BASE}/projects/", timeout=10)

            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test(
                        "Project Listing",
                        True,
                        f"Retrieved {len(data)} projects",
                        {"count": len(data)},
                    )
                    return True
                else:
                    self.log_test("Project Listing", False, "Response is not a list")
                    return False
            else:
                self.log_test("Project Listing", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Project Listing", False, f"Exception: {e}")
            return False

    def test_api_documentation(self):
        """Test API documentation availability"""
        try:
            response = requests.get(f"{BASE_URL}/docs", timeout=5)
            if response.status_code == 200:
                self.log_test("API Documentation", True, "Documentation is accessible")
                return True
            else:
                self.log_test(
                    "API Documentation", False, f"HTTP {response.status_code}"
                )
                return False
        except Exception as e:
            self.log_test("API Documentation", False, f"Exception: {e}")
            return False

    def run_all_tests(self):
        """Run all tests"""
        print("=" * 60)
        print("Multi-Agent AI System - Comprehensive Test Suite")
        print("=" * 60)

        tests = [
            ("Health Check", self.test_health_check),
            ("System Status", self.test_system_status),
            ("API Documentation", self.test_api_documentation),
            ("Project Creation", self.test_project_creation),
            ("Project Processing", self.test_project_processing),
            ("Project Results", self.test_project_results),
            ("Project Listing", self.test_project_listing),
        ]

        passed = 0
        total = len(tests)

        for test_name, test_func in tests:
            print(f"\nRunning {test_name}...")
            if test_func():
                passed += 1

        print("\n" + "=" * 60)
        print(f"Test Results: {passed}/{total} tests passed")
        print("=" * 60)

        if passed == total:
            print(
                "🎉 ALL TESTS PASSED! The Multi-Agent AI System is working correctly."
            )
            return True
        else:
            print(f"❌ {total - passed} tests failed. Please check the system.")
            return False

    def generate_report(self):
        """Generate detailed test report"""
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_tests": len(self.test_results),
            "passed_tests": sum(1 for r in self.test_results if r["success"]),
            "failed_tests": sum(1 for r in self.test_results if not r["success"]),
            "test_details": self.test_results,
        }

        with open("test_report.json", "w") as f:
            json.dump(report, f, indent=2)

        print("\nDetailed test report saved to: test_report.json")
        return report


def main():
    """Main test function"""
    tester = SystemTester()

    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print(
                "❌ Server is not running or not responding. Please start the server first."
            )
            sys.exit(1)
    except Exception as e:
        print(
            f"❌ Cannot connect to server at {BASE_URL}. Please start the server first."
        )
        print(f"Error: {e}")
        sys.exit(1)

    # Run tests
    success = tester.run_all_tests()

    # Generate report
    tester.generate_report()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
