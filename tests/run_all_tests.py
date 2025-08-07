#!/usr/bin/env python3
"""
Comprehensive test runner for the Bikes TextToSQL Agent project.
Runs all tests from the organized test structure.
"""

import os
import sys
import subprocess
import time
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_tests(test_type, test_path):
    """Run tests of a specific type."""
    print(f"\n{'='*60}")
    print(f"🧪 Running {test_type.upper()} Tests")
    print(f"{'='*60}")
    
    if not os.path.exists(test_path):
        print(f"❌ Test path not found: {test_path}")
        return False
    
    # Get all test files
    test_files = []
    for root, dirs, files in os.walk(test_path):
        for file in files:
            if file.startswith('test_') and file.endswith('.py'):
                test_files.append(os.path.join(root, file))
    
    if not test_files:
        print(f"⚠️  No test files found in {test_path}")
        return True
    
    print(f"📁 Found {len(test_files)} test files:")
    for test_file in test_files:
        print(f"   - {os.path.relpath(test_file, project_root)}")
    
    # Run tests
    success = True
    for test_file in test_files:
        print(f"\n🔍 Running: {os.path.basename(test_file)}")
        try:
            result = subprocess.run([sys.executable, test_file], 
                                  capture_output=True, text=True, cwd=project_root)
            
            if result.returncode == 0:
                print(f"✅ {os.path.basename(test_file)} - PASSED")
                if result.stdout.strip():
                    print(f"   Output: {result.stdout.strip()}")
            else:
                print(f"❌ {os.path.basename(test_file)} - FAILED")
                print(f"   Error: {result.stderr.strip()}")
                success = False
                
        except Exception as e:
            print(f"❌ {os.path.basename(test_file)} - ERROR: {e}")
            success = False
    
    return success

def run_pytest_tests(test_path):
    """Run tests using pytest if available."""
    try:
        import pytest
        print(f"\n{'='*60}")
        print(f"🧪 Running pytest on {test_path}")
        print(f"{'='*60}")
        
        result = subprocess.run([sys.executable, '-m', 'pytest', test_path, '-v'], 
                              capture_output=True, text=True, cwd=project_root)
        
        print(result.stdout)
        if result.stderr:
            print(f"Errors: {result.stderr}")
        
        return result.returncode == 0
    except ImportError:
        print("⚠️  pytest not available, skipping pytest tests")
        return True

def main():
    """Main test runner function."""
    print("🏍️ Bikes TextToSQL Agent - Test Suite")
    print("="*60)
    
    # Test paths
    test_paths = {
        'unit': 'tests/unit',
        'integration': 'tests/integration', 
        'performance': 'tests/performance'
    }
    
    overall_success = True
    
    # Run each test type
    for test_type, test_path in test_paths.items():
        success = run_tests(test_type, test_path)
        if not success:
            overall_success = False
    
    # Run pytest tests if available
    pytest_success = run_pytest_tests('tests/')
    if not pytest_success:
        overall_success = False
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 Test Summary")
    print(f"{'='*60}")
    
    if overall_success:
        print("🎉 All tests passed successfully!")
        print("✅ Project is ready for deployment")
    else:
        print("❌ Some tests failed")
        print("🔧 Please fix the failing tests before proceeding")
    
    return 0 if overall_success else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 