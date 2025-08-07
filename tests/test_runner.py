"""
Test Runner for TextToSQL Agent v2 Components

This script runs all component tests and generates comprehensive reports
to ensure each component meets quality standards before integration.

Author: TextToSQL Agent v2
Created: 2025-01-06
"""

import sys
import os
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple
import time

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class ComponentTestRunner:
    """Test runner for individual components with detailed reporting."""
    
    def __init__(self):
        self.results: Dict[str, Dict] = {}
        self.start_time = time.time()
    
    def run_component_tests(self, component_name: str, test_file: str) -> Dict:
        """
        Run tests for a specific component and return results.
        
        Args:
            component_name: Name of the component being tested
            test_file: Path to the test file
            
        Returns:
            Dictionary with test results
        """
        print(f"\n🧪 Testing Component: {component_name}")
        print("=" * 50)
        
        start_time = time.time()
        
        try:
            # Run pytest with coverage and verbose output
            cmd = [
                "python", "-m", "pytest", 
                test_file,
                "-v",
                "--tb=short",
                f"--cov={component_name}",
                "--cov-report=term",
                "--cov-report=html:htmlcov/" + component_name,
                "--cov-fail-under=90"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=project_root
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Parse results
            output_lines = result.stdout.split('\n')
            error_lines = result.stderr.split('\n')
            
            # Extract test statistics
            passed_tests = len([line for line in output_lines if " PASSED " in line])
            failed_tests = len([line for line in output_lines if " FAILED " in line])
            total_tests = passed_tests + failed_tests
            
            # Extract coverage percentage
            coverage_line = [line for line in output_lines if "TOTAL" in line and "%" in line]
            coverage_percent = 0
            if coverage_line:
                try:
                    coverage_percent = int(coverage_line[0].split()[-1].replace('%', ''))
                except:
                    coverage_percent = 0
            
            test_result = {
                "component": component_name,
                "success": result.returncode == 0,
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "coverage_percent": coverage_percent,
                "duration": duration,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
            # Print summary
            if test_result["success"]:
                print(f"✅ {component_name} tests PASSED")
                print(f"   Tests: {passed_tests}/{total_tests} passed")
                print(f"   Coverage: {coverage_percent}%")
                print(f"   Duration: {duration:.2f}s")
            else:
                print(f"❌ {component_name} tests FAILED")
                print(f"   Tests: {passed_tests}/{total_tests} passed")
                print(f"   Coverage: {coverage_percent}%")
                print(f"   Duration: {duration:.2f}s")
                print("   Error output:")
                print(result.stderr)
            
            return test_result
            
        except Exception as e:
            return {
                "component": component_name,
                "success": False,
                "error": str(e),
                "duration": time.time() - start_time
            }
    
    def validate_component(self, component_name: str, test_result: Dict) -> Tuple[bool, List[str]]:
        """
        Validate that a component meets all quality criteria.
        
        Args:
            component_name: Name of the component
            test_result: Test results dictionary
            
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        # Check if tests passed
        if not test_result.get("success", False):
            issues.append("❌ Tests failed")
        
        # Check test coverage
        coverage = test_result.get("coverage_percent", 0)
        if coverage < 90:
            issues.append(f"❌ Test coverage too low: {coverage}% (required: 90%)")
        
        # Check number of tests
        total_tests = test_result.get("total_tests", 0)
        if total_tests < 5:
            issues.append(f"❌ Insufficient tests: {total_tests} (recommended: 5+)")
        
        # Check for failed tests
        failed_tests = test_result.get("failed_tests", 0)
        if failed_tests > 0:
            issues.append(f"❌ {failed_tests} tests failed")
        
        is_valid = len(issues) == 0
        
        return is_valid, issues
    
    def generate_report(self) -> str:
        """Generate a comprehensive test report."""
        total_time = time.time() - self.start_time
        
        report = []
        report.append("🧪 TextToSQL Agent v2 - Component Test Report")
        report.append("=" * 60)
        report.append(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total Duration: {total_time:.2f}s")
        report.append("")
        
        total_components = len(self.results)
        passed_components = len([r for r in self.results.values() if r.get("success", False)])
        
        report.append(f"📊 Overall Summary:")
        report.append(f"   Components Tested: {total_components}")
        report.append(f"   Components Passed: {passed_components}")
        report.append(f"   Success Rate: {(passed_components/total_components*100):.1f}%" if total_components > 0 else "   Success Rate: 0%")
        report.append("")
        
        # Component details
        for component_name, result in self.results.items():
            report.append(f"🔧 Component: {component_name}")
            report.append("-" * 30)
            
            if result.get("success", False):
                report.append("✅ Status: PASSED")
            else:
                report.append("❌ Status: FAILED")
            
            if "total_tests" in result:
                report.append(f"   Tests: {result['passed_tests']}/{result['total_tests']} passed")
                report.append(f"   Coverage: {result['coverage_percent']}%")
                report.append(f"   Duration: {result['duration']:.2f}s")
            
            # Validation
            is_valid, issues = self.validate_component(component_name, result)
            if is_valid:
                report.append("✅ Validation: PASSED - Ready for integration")
            else:
                report.append("❌ Validation: FAILED")
                for issue in issues:
                    report.append(f"   {issue}")
            
            report.append("")
        
        return "\n".join(report)
    
    def run_all_tests(self) -> bool:
        """Run all component tests and return overall success."""
        print("🚀 Starting Component Test Suite")
        print("=" * 60)
        
        # Define components to test
        components = [
            ("config", "config/test_settings.py"),
            # Add more components as they are built
        ]
        
        all_passed = True
        
        for component_name, test_file in components:
            test_file_path = project_root / test_file
            
            if not test_file_path.exists():
                print(f"⚠️  Test file not found: {test_file}")
                self.results[component_name] = {
                    "success": False,
                    "error": "Test file not found"
                }
                all_passed = False
                continue
            
            result = self.run_component_tests(component_name, str(test_file_path))
            self.results[component_name] = result
            
            if not result.get("success", False):
                all_passed = False
        
        # Generate and display report
        print("\n" + self.generate_report())
        
        return all_passed


def main():
    """Main function to run component tests."""
    runner = ComponentTestRunner()
    
    try:
        success = runner.run_all_tests()
        
        if success:
            print("\n🎉 All component tests passed! Ready for integration.")
            sys.exit(0)
        else:
            print("\n💥 Some component tests failed. Please fix issues before proceeding.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️  Test run interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test runner error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 