#include "cpp_headers/BooPHF.h"
#include <algorithm>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <map>
#include <set>
#include <sstream>
#include <string>
#include <vector>

using boophf_t = boomphf::mphf<uint64_t, boomphf::SingleHashFunctor<uint64_t>>;

// Load test keys from CSV (single column: key)
std::vector<uint64_t> load_test_keys(const std::string& csv_file)
{
	std::vector<uint64_t> keys;
	std::ifstream infile(csv_file);
	if (!infile)
	{
		std::cerr << "Failed to open CSV file: " << csv_file << "\n";
		return keys;
	}

	std::string line;
	std::getline(infile, line); // Skip header

	while (std::getline(infile, line))
	{
		if (line.empty())
			continue;
		uint64_t key = std::stoull(line);
		keys.push_back(key);
	}

	return keys;
}

// Load hash results from CSV for comparison
std::map<uint64_t, uint64_t> load_hashes_from_csv(const std::string& csv_file)
{
	std::map<uint64_t, uint64_t> hashes;
	std::ifstream infile(csv_file);
	if (!infile)
	{
		std::cerr << "Failed to open hash CSV file: " << csv_file << "\n";
		return hashes;
	}

	std::string line;
	std::getline(infile, line); // Skip header

	while (std::getline(infile, line))
	{
		std::istringstream iss(line);
		std::string key_str, hash_str;

		if (!std::getline(iss, key_str, ','))
			continue;
		if (!std::getline(iss, hash_str, ','))
			continue;

		uint64_t key = std::stoull(key_str);
		uint64_t hash_val = std::stoull(hash_str);
		hashes[key] = hash_val;
	}

	return hashes;
}

// Test 1: Build C++ MPHF from test keys and export
bool test_cpp_build_and_export()
{
	std::cout << "\n=== Test 1: C++ Build and Export ===\n";

	// Load test keys from out/
	auto keys = load_test_keys("out/test_keys.csv");
	if (keys.empty())
	{
		std::cerr << " Failed to load test keys\n";
		return false;
	}
	std::cout << " Loaded " << keys.size() << " test keys\n";

	// Build MPHF with gamma=2.0
	std::cout << "Building C++ MPHF...\n";
	boophf_t bphf(keys.size(), keys, 1, 2.0, false, false);
	std::cout << " Built MPHF in C++\n";

	// Save to binary file (into out/)
	std::ofstream os("out/test_data_cpp.mphf", std::ios::binary);
	if (!os)
	{
		std::cerr << " Failed to create output file\n";
		return false;
	}
	bphf.save(os);
	os.close();
	std::cout << " Saved binary to: test_data_cpp.mphf\n";

	// Save hash results to CSV
	std::ofstream csv("out/test_data_cpp_hashes.csv");
	if (!csv)
	{
		std::cerr << " Failed to create CSV file\n";
		return false;
	}
	csv << "key,hash_value\n";
	for (uint64_t key : keys)
	{
		uint64_t hash_val = bphf.lookup(key);
		csv << key << "," << hash_val << "\n";
	}
	csv.close();
	std::cout << " Saved hash results to: test_data_cpp_hashes.csv\n";

	// Sample lookups
	std::cout << "\nSample lookups:\n";
	for (size_t i : { size_t(0), keys.size() / 2, keys.size() - 1 })
	{
		uint64_t key = keys[i];
		uint64_t hash_val = bphf.lookup(key);
		std::cout << "  lookup(" << key << ") = " << hash_val << "\n";
	}

	std::cout << "\n C++ export complete!\n";
	return true;
}

// Test 2: Load Python MPHF binary and verify binary compatibility
bool test_load_python_binary()
{
	std::cout << "\n=== Test 2: Load Python Binary (Binary Compatibility Test) ===\n";

	// Load test keys (use out/ to avoid polluting directory)
	auto keys = load_test_keys("out/test_keys.csv");
	if (keys.empty())
	{
		std::cerr << " Failed to load test keys\n";
		return false;
	}
	std::cout << " Loaded " << keys.size() << " test keys\n";

	// Load the reference hash assignments computed in Python
	auto python_hashes = load_hashes_from_csv("out/test_data_py_hashes.csv");
	if (python_hashes.empty())
	{
		std::cerr << " Failed to load Python hash results (run export_test_data.py first)\n";
		return false;
	}
	if (python_hashes.size() != keys.size())
	{
		std::cerr << " Hash reference size mismatch: expected " << keys.size()
		          << ", got " << python_hashes.size() << "\n";
	}

	// Load MPHF from Python binary
	std::ifstream is("out/test_data_py.mphf", std::ios::binary);
	if (!is)
	{
		std::cerr << " Failed to open Python binary file\n";
		std::cerr << "  Please run: python export_test_data.py\n";
		return false;
	}

	boophf_t bphf;
	bphf.load(is);
	is.close();
	std::cout << " Loaded MPHF from Python binary\n";

	// Verify MPHF properties
	std::cout << "Verifying MPHF properties...\n";

	std::set<uint64_t> hash_values;
	int range_errors = 0;
	int mismatch_errors = 0;
	const int max_report = 10;

	for (uint64_t key : keys)
	{
		auto expected_it = python_hashes.find(key);
		if (expected_it == python_hashes.end())
		{
			std::cerr << " Missing Python hash for key " << key << "\n";
			return false;
		}

		uint64_t hash_val = bphf.lookup(key);

		// Check range
		if (hash_val >= keys.size())
		{
			if (range_errors < max_report)
			{
				std::cerr << " Out of range for key " << key << ": " << hash_val
				          << " not in [0, " << keys.size() - 1 << "]\n";
			}
			++range_errors;
		}
		else
		{
			hash_values.insert(hash_val);
		}

		// Ensure the lookup matches the Python assignment
		if (hash_val != expected_it->second)
		{
			if (mismatch_errors < max_report)
			{
				std::cerr << " Hash mismatch for key " << key << ": Python="
				          << expected_it->second << ", C++=" << hash_val << "\n";
			}
			++mismatch_errors;
		}
	}

	if (range_errors > 0)
	{
		std::cerr << " Binary compatibility test failed due to range errors ("
		          << range_errors << ")\n";
		return false;
	}

	if (hash_values.size() != keys.size())
	{
		std::cerr << " Hash collision detected!\n";
		std::cerr << "  Expected " << keys.size() << " unique hashes, got "
		          << hash_values.size() << "\n";
		return false;
	}

	if (mismatch_errors > 0)
	{
		std::cerr << " Hash mismatch detected (" << mismatch_errors
		          << ") between Python and C++ lookups\n";
		return false;
	}

	std::cout << " All " << keys.size() << " keys can be looked up\n";
	std::cout << " All hash values in valid range [0, " << keys.size() - 1 << "]\n";
	std::cout << " Lookup results match Python assignments exactly\n";
	std::cout << " Binary compatibility verified!\n";
	return true;
}

// Test 3: Compare hash values between Python and C++
bool test_compare_hash_values()
{
	std::cout << "\n=== Test 3: Compare Hash Values (Python vs C++) ===\n";

	// Load Python hash results (from out/)
	auto py_hashes = load_hashes_from_csv("out/test_data_py_hashes.csv");
	if (py_hashes.empty())
	{
		std::cerr << " Failed to load Python hash results\n";
		return false;
	}
	std::cout << " Loaded Python hash results: " << py_hashes.size() << " entries\n";

	// Load C++ hash results (from out/)
	auto cpp_hashes = load_hashes_from_csv("out/test_data_cpp_hashes.csv");
	if (cpp_hashes.empty())
	{
		std::cerr << " Failed to load C++ hash results\n";
		return false;
	}
	std::cout << " Loaded C++ hash results: " << cpp_hashes.size() << " entries\n";

	// Compare
	size_t matches = 0;
	size_t mismatches = 0;
	size_t samples_shown = 0;
	const size_t max_samples = 10;

	std::cout << "\nComparing hash values...\n";

	for (const auto& [key, py_hash] : py_hashes)
	{
		auto it = cpp_hashes.find(key);
		if (it == cpp_hashes.end())
		{
			std::cerr << " Key " << key << " not found in C++ results\n";
			continue;
		}

		uint64_t cpp_hash = it->second;
		if (py_hash == cpp_hash)
		{
			matches++;
			if (samples_shown < 3)
			{
				std::cout << "  Match:     key=" << key << " -> hash=" << py_hash << "\n";
				samples_shown++;
			}
		}
		else
		{
			mismatches++;
			if (samples_shown < max_samples)
			{
				std::cout << "  Mismatch:  key=" << key << " -> Python=" << py_hash
				          << ", C++=" << cpp_hash << "\n";
				samples_shown++;
			}
		}
	}

	// Summary
	std::cout << "\nComparison Summary:\n";
	std::cout << "  Total keys:   " << py_hashes.size() << "\n";
	std::cout << "  Matches:      " << matches << " ("
	          << (100.0 * matches / py_hashes.size()) << "%)\n";
	std::cout << "  Mismatches:   " << mismatches << " ("
	          << (100.0 * mismatches / py_hashes.size()) << "%)\n";

	if (matches == py_hashes.size())
	{
		std::cout << "\n Perfect match! Python and C++ produce identical hashes.\n";
	}
	else if (mismatches == py_hashes.size())
	{
		std::cout << "\n Different hash values (expected for independent MPHF builds)\n";
		std::cout << "  Both implementations produce valid MPHFs with different assignments.\n";
	}
	else
	{
		std::cout << "\n Partial match (some keys have same hash values)\n";
	}

	return true;
}

int main()
{
	std::cout << "===========================================================\n";
	std::cout << "   Cross-Language Binary Compatibility Test (C++ Side)   \n";
	std::cout << "===========================================================\n";

	bool all_passed = true;

	// Test 1: Build C++ MPHF and export
	if (!test_cpp_build_and_export())
	{
		std::cerr << "\n Test 1 failed\n";
		all_passed = false;
	}

	// Test 2: Load Python binary
	if (!test_load_python_binary())
	{
		std::cerr << "\n Test 2 failed\n";
		all_passed = false;
	}

	// Test 3: Compare hash values
	if (!test_compare_hash_values())
	{
		std::cerr << "\n Test 3 failed\n";
		all_passed = false;
	}

	// Summary
	std::cout << "\n===========================================================\n";
	if (all_passed)
	{
		std::cout << " All tests passed!\n";
		std::cout << "===========================================================\n";
		return 0;
	}
	else
	{
		std::cout << " Some tests failed\n";
		std::cout << "===========================================================\n";
		return 1;
	}
}
