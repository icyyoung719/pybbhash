#!/usr/bin/env python3
"""Run complete cross-language binary compatibility test suite."""

import sys
import os
import subprocess
import platform

def run_command(cmd, description):
    """Run a command and report results."""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")
    print(f"Running: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, capture_output=False)
    
    if result.returncode == 0:
        print(f"✓ {description} - PASSED")
        return True
    else:
        print(f"✗ {description} - FAILED")
        return False


def main():
    print("\n" + "="*60)
    print("Cross-Language Binary Compatibility Test Suite")
    print("="*60)
    
    # Change to cpp-bbhash directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    print(f"\nWorking directory: {os.getcwd()}")
    
    results = []
    
    # Step 1: Generate Python test data
    results.append(run_command(
        [sys.executable, "export_test_data.py"],
        "Step 1: Generate Python test data"
    ))
    
    if not results[-1]:
        print("\n✗ Failed to generate Python test data. Aborting.")
        return False
    
    # Step 2: Compile C++ test
    print(f"\n{'='*60}")
    print("Step 2: Compile C++ test")
    print(f"{'='*60}")
    
    # Determine compiler based on platform
    if platform.system() == "Windows":
        # Try to use cl.exe (MSVC) or g++ if available
        compile_cmd = [
            "cl.exe", "/std:c++17", "/EHsc", "/W3",
            "test_min.cpp", "/Fe:test_min.exe",
            "/I."
        ]
        executable = "test_min.exe"
        
        # Check if cl.exe is available
        cl_check = subprocess.run(["where", "cl"], capture_output=True)
        if cl_check.returncode != 0:
            # Fall back to g++
            print("MSVC not found, trying g++...")
            compile_cmd = [
                "g++", "-std=c++17", "-O2", "-Wall",
                "test_min.cpp", "-o", "test_min.exe",
                "-I."
            ]
    else:
        compile_cmd = [
            "g++", "-std=c++17", "-O2", "-Wall",
            "test_min.cpp", "-o", "test_min",
            "-I."
        ]
        executable = "./test_min"
    
    print(f"Compile command: {' '.join(compile_cmd)}")
    compile_result = subprocess.run(compile_cmd, capture_output=True, text=True)
    
    if compile_result.returncode != 0:
        print("✗ Compilation failed!")
        print(compile_result.stdout)
        print(compile_result.stderr)
        print("\nNote: You may need to compile manually with your C++ compiler.")
        print("Example for g++:")
        print("  g++ -std=c++17 -O2 test_min.cpp -o test_min -I.")
        print("Example for MSVC:")
        print("  cl /std:c++17 /EHsc test_min.cpp /I.")
        return False
    else:
        print("✓ Compilation succeeded")
        results.append(True)
    
    # Step 3: Run C++ test (includes both Python→C++ and C++→Python)
    if platform.system() == "Windows":
        cpp_cmd = ["test_min.exe"]
    else:
        cpp_cmd = ["./test_min"]
    
    results.append(run_command(
        cpp_cmd,
        "Step 3: Run C++ tests (Python→C++ and C++→Python)"
    ))
    
    if not results[-1]:
        print("\n✗ C++ test failed. Check the output above.")
        return False
    
    # Step 4: Verify C++ export in Python
    results.append(run_command(
        [sys.executable, "verify_cpp_export.py"],
        "Step 4: Verify C++ export in Python"
    ))
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUITE SUMMARY")
    print("="*60)
    
    test_names = [
        "Python data generation",
        "C++ compilation",
        "C++ tests (Python→C++ and C++→Python)",
        "Python verification of C++ export"
    ]
    
    all_passed = True
    for i, (name, passed) in enumerate(zip(test_names, results), 1):
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{i}. {name}: {status}")
        if not passed:
            all_passed = False
    
    print("="*60)
    if all_passed:
        print("✓ ALL TESTS PASSED!")
        print("\nBinary format compatibility verified:")
        print("  • Python → C++ loading works correctly")
        print("  • C++ → Python loading works correctly")
        print("  • Hash values match across languages")
        return True
    else:
        print("✗ SOME TESTS FAILED")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
