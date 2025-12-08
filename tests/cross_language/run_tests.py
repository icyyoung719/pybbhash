#!/usr/bin/env python3
"""Run complete cross-language binary compatibility test suite.

Test flow:
1. Generate test keys (test_keys.csv) - fixed seed for reproducibility
2. Python builds MPHF and exports binary + hashes
3. C++ builds MPHF and exports binary + hashes, also loads Python binary
4. Python loads C++ binary
5. Compare hash values between Python and C++
"""

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
        print(f"[OK] {description} - PASSED")
        return True
    else:
        print(f"[ERROR] {description} - FAILED")
        return False


def main():
    print("\n" + "="*60)
    print("Cross-Language Binary Compatibility Test Suite")
    print("="*60)

    # Change to test directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    print(f"\nWorking directory: {os.getcwd()}")
    # Ensure output directory exists
    out_dir = os.path.join(script_dir, 'out')
    os.makedirs(out_dir, exist_ok=True)

    results = []

    # Step 0: Generate test keys
    results.append(run_command(
        [sys.executable, "generate_test_keys.py"],
        "Step 0: Generate test keys"
    ))

    if not results[-1]:
        print("\n[ERROR] Failed to generate test keys. Aborting.")
        return False

    # Step 1: Python builds MPHF and exports
    results.append(run_command(
        [sys.executable, "export_test_data.py"],
        "Step 1: Python build and export"
    ))

    if not results[-1]:
        print("\n[ERROR] Failed to generate Python MPHF. Aborting.")
        return False

    # Step 2: Compile C++ test
    print(f"\n{'='*60}")
    print("Step 2: Compile C++ test")
    print(f"{'='*60}")

    # Check if g++ is available
    gpp_check = subprocess.run(["g++", "--version"], capture_output=True)
    if gpp_check.returncode != 0 and platform.system() == "Windows":
        # Fall back to MSVC on Windows
        print("g++ not found, trying MSVC...")
        compile_cmd = [
            "cl.exe", "/std:c++17", "/EHsc", "/W3",
            "test_compatibility.cpp",
            f"/Fe:{os.path.join(out_dir, 'test_compatibility.exe')}",
            f"/Fo:{os.path.join(out_dir, 'test_compatibility.obj')}",
            "/I.", "/I.\\cpp_headers"
        ]
        executable = os.path.join(out_dir, 'test_compatibility.exe')
    else:
        compile_cmd = [
            "g++", "-std=c++17", "-O2", "-Wall",
            "test_compatibility.cpp", "-o", os.path.join(out_dir, 'test_compatibility.exe' if platform.system() == "Windows" else 'test_compatibility'),
            "-I.", "-I./cpp_headers"
        ]
        executable = os.path.join(out_dir, 'test_compatibility.exe' if platform.system() == "Windows" else 'test_compatibility')

    print(f"Compile command: {' '.join(compile_cmd)}")
    compile_result = subprocess.run(compile_cmd, capture_output=True, text=True)

    if compile_result.returncode != 0:
        print("[ERROR] Compilation failed!")
        print(compile_result.stdout)
        print(compile_result.stderr)
        print("\nNote: You may need to compile manually with your C++ compiler.")
        print("Example for g++:")
        print("  g++ -std=c++17 -O2 test_compatibility.cpp -o out/test_compatibility -I. -I./cpp_headers")
        print("Example for MSVC:")
        print(f"  cl /std:c++17 /EHsc test_compatibility.cpp /Fe:{os.path.join(out_dir,'test_compatibility.exe')} /I. /I.\\cpp_headers")
        return False
    else:
        print("[OK] Compilation succeeded")
        results.append(True)

    # Step 3: Run C++ test (builds C++ MPHF, loads Python binary, compares hashes)
    cpp_cmd = [executable]

    results.append(run_command(
        cpp_cmd,
        "Step 3: Run C++ tests"
    ))

    if not results[-1]:
        print("\n[ERROR] C++ test failed. Check the output above.")
        return False

    # Step 4: Python loads C++ binary
    results.append(run_command(
        [sys.executable, "verify_cpp_export.py"],
        "Step 4: Python loads C++ binary"
    ))

    # Print summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    passed = sum(results)
    total = len(results)
    print(f"Tests passed: {passed}/{total}")

    if all(results):
        print("\n[OK] ALL TESTS PASSED!")
        print("\nKey findings:")
        print("  1. Binary format is fully compatible between Python and C++")
        print("  2. Both implementations can load each other's MPHF files")
        print("  3. All keys can be looked up successfully")
        print("  4. Hash value differences (if any) are expected and acceptable")
        return True
    else:
        print("\n[ERROR] SOME TESTS FAILED")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
