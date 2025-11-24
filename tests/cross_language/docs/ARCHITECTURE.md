# Cross-Language Test Architecture

## Test Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    run_cross_language_tests.py                  │
│                     (Master Orchestrator)                        │
└─────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
        ┌─────────────────────────────────────────────────┐
        │        Step 1: Generate Python Test Data        │
        │         (export_test_data.py)                   │
        └─────────────────────────────────────────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    ▼                           ▼
        ┏━━━━━━━━━━━━━━━━━━┓        ┏━━━━━━━━━━━━━━━━━━┓
        ┃ test_data_py.mphf┃        ┃ test_data_py.csv ┃
        ┃  (Binary File)   ┃        ┃  (Expected Values)┃
        ┗━━━━━━━━━━━━━━━━━━┛        ┗━━━━━━━━━━━━━━━━━━┛
                    │                           │
                    └─────────────┬─────────────┘
                                  ▼
        ┌─────────────────────────────────────────────────┐
        │        Step 2: Compile C++ Test Program         │
        │    (g++ -std=c++17 test_min.cpp -o test_min)   │
        └─────────────────────────────────────────────────┘
                                  │
                                  ▼
        ┌─────────────────────────────────────────────────┐
        │           Step 3: Run C++ Test Program          │
        │                (./test_min)                     │
        └─────────────────────────────────────────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    ▼                           ▼
        ┏━━━━━━━━━━━━━━━━━━━┓       ┏━━━━━━━━━━━━━━━━━━━┓
        ┃ test_data_cpp.mphf┃       ┃ test_data_cpp.csv ┃
        ┃   (Binary File)   ┃       ┃  (Expected Values) ┃
        ┗━━━━━━━━━━━━━━━━━━━┛       ┗━━━━━━━━━━━━━━━━━━━┛
                    │                           │
                    └─────────────┬─────────────┘
                                  ▼
        ┌─────────────────────────────────────────────────┐
        │    Step 4: Verify C++ Export in Python          │
        │         (verify_cpp_export.py)                  │
        └─────────────────────────────────────────────────┘
                                  │
                                  ▼
        ┌─────────────────────────────────────────────────┐
        │              ✅ All Tests Passed                 │
        └─────────────────────────────────────────────────┘
```

## Test 1: Python → C++ (in test_min.cpp)

```
┌──────────────┐
│   Python     │
│   Build MPHF │
│   (1000 keys)│
└──────┬───────┘
       │
       │ save()
       ▼
┏━━━━━━━━━━━━━━━┓
┃test_data_py   ┃
┃  .mphf        ┃ ─────────┐
┗━━━━━━━━━━━━━━━┛          │
                           │
┏━━━━━━━━━━━━━━━┓          │
┃test_data_py   ┃          │
┃  .csv         ┃ ───┐     │
┗━━━━━━━━━━━━━━━┛    │     │
                     │     │
                     ▼     ▼
              ┌──────────────────┐
              │   C++ Program    │
              │   - Load MPHF    │
              │   - Load CSV     │
              │   - Compare all  │
              │     lookups      │
              └────────┬─────────┘
                       │
                       ▼
                ✅ 1000/1000 Match
```

## Test 2: C++ → Python (in test_min.cpp + verify_cpp_export.py)

```
┌──────────────┐
│    C++       │
│  Build MPHF  │
│  (1000 keys) │
└──────┬───────┘
       │
       │ save()
       ▼
┏━━━━━━━━━━━━━━━┓
┃test_data_cpp  ┃
┃  .mphf        ┃ ─────────┐
┗━━━━━━━━━━━━━━━┛          │
                           │
┏━━━━━━━━━━━━━━━┓          │
┃test_data_cpp  ┃          │
┃  .csv         ┃ ───┐     │
┗━━━━━━━━━━━━━━━┛    │     │
                     │     │
                     ▼     ▼
              ┌──────────────────┐
              │  Python Script   │
              │  - Load MPHF     │
              │  - Load CSV      │
              │  - Compare all   │
              │    lookups       │
              └────────┬─────────┘
                       │
                       ▼
                ✅ 1000/1000 Match
```

## Binary Format Compatibility

```
┌─────────────────────────────────────────────┐
│           MPHF Binary File Format           │
├─────────────────────────────────────────────┤
│  Header (28 bytes)                          │
│  ┌──────────────────────────────────────┐   │
│  │ _gamma          (double, 8 bytes)    │   │
│  │ _nb_levels      (uint32_t, 4 bytes)  │   │
│  │ _lastbitsetrank (uint64_t, 8 bytes)  │   │
│  │ _nelem          (uint64_t, 8 bytes)  │   │
│  └──────────────────────────────────────┘   │
│                                             │
│  Level Bitsets (25 levels × variable size) │
│  ┌──────────────────────────────────────┐   │
│  │ For each level:                      │   │
│  │   - _size      (uint64_t, 8 bytes)   │   │
│  │   - _nchar     (uint64_t, 8 bytes)   │   │
│  │   - _bitArray  (uint64_t[], variable)│   │
│  │   - ranks_size (uint64_t, 8 bytes)   │   │
│  │   - _ranks     (uint64_t[], variable)│   │
│  └──────────────────────────────────────┘   │
│                                             │
│  Final Hash Table (variable size)          │
│  ┌──────────────────────────────────────┐   │
│  │ final_hash_size (uint64_t, 8 bytes)  │   │
│  │ For each entry:                      │   │
│  │   - key   (uint64_t, 8 bytes)        │   │
│  │   - value (uint64_t, 8 bytes)        │   │
│  └──────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
         │                         │
         ▼                         ▼
    ┌─────────┐              ┌─────────┐
    │ Python  │              │   C++   │
    │  Read   │◄────────────►│  Read   │
    │  Write  │              │  Write  │
    └─────────┘              └─────────┘
       100% Compatible
```

## CI/CD Pipeline

```
┌─────────────────────────────────────────┐
│       GitHub Actions Workflow           │
└─────────────────────────────────────────┘
                  │
    ┌─────────────┼─────────────┐
    ▼             ▼             ▼
┌────────┐  ┌─────────┐  ┌──────────┐
│  Test  │  │ Cross-  │  │  Build   │
│  Job   │  │Language │  │   Job    │
│(pytest)│  │  Test   │  │          │
└────────┘  └─────────┘  └──────────┘
                  │
                  ▼
    ┌─────────────────────────────┐
    │ - Setup Python 3.11         │
    │ - Install pybbhash          │
    │ - Install g++               │
    │ - Run cross-language tests  │
    └─────────────────────────────┘
                  │
        ┌─────────┴─────────┐
        ▼                   ▼
    ✅ Pass              ❌ Fail
        │                   │
        ▼                   ▼
   Continue            Block merge
   pipeline            to main
```

## File Dependencies

```
cpp-bbhash/
│
├── BooPHF.h ◄─────────────┐
├── bitvector.hpp ◄────┐   │
├── platform_time.h ◄──┼───┼── Included by
├── progress.hpp ◄─────┘   │   test_min.cpp
│                          │
├── test_min.cpp ──────────┘
│   ├── Test 1: Load Python MPHF
│   └── Test 2: Create C++ MPHF
│
├── export_test_data.py
│   └── Generates: test_data_py.{mphf,csv}
│
├── verify_cpp_export.py
│   └── Loads: test_data_cpp.{mphf,csv}
│
└── run_cross_language_tests.py
    ├── Calls: export_test_data.py
    ├── Compiles: test_min.cpp
    ├── Runs: test_min
    └── Calls: verify_cpp_export.py
```

## Verification Matrix

```
┌─────────────┬──────────────┬──────────────┐
│   Action    │   Creator    │   Verifier   │
├─────────────┼──────────────┼──────────────┤
│ Build MPHF  │   Python     │     C++      │
│ Save Binary │   Python     │     C++      │
│ Load Binary │     C++      │   Python     │
│ Lookup Keys │     Both     │     Both     │
├─────────────┼──────────────┼──────────────┤
│ Build MPHF  │     C++      │   Python     │
│ Save Binary │     C++      │   Python     │
│ Load Binary │   Python     │     C++      │
│ Lookup Keys │     Both     │     Both     │
└─────────────┴──────────────┴──────────────┘
```

## Success Criteria

✅ All 1000 keys produce identical hash values
✅ Binary files load without errors
✅ Metadata matches (_gamma, _nb_levels, _nelem, _lastbitsetrank)
✅ No hash collisions (perfect hash maintained)
✅ Tests pass on Linux (CI), Windows, and macOS
✅ Byte-for-byte format compatibility verified
