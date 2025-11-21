#include "BooPHF.h"
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <map>
#include <sstream>
#include <string>
#include <vector>

using boophf_t = boomphf::mphf<uint64_t, boomphf::SingleHashFunctor<uint64_t>>;

// Load keys from CSV (we only need the keys, not the hash values)
std::vector<uint64_t> load_keys_from_csv(const std::string& csv_file)
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
		std::istringstream iss(line);
		std::string key_str, val_str;

		if (!std::getline(iss, key_str, ','))
			continue;
		// Skip the hash value column
		std::getline(iss, val_str, ',');

		uint64_t key = std::stoull(key_str);
		keys.push_back(key);
	}

	return keys;
}

// Test 1: Load Python-generated MPHF and verify MPHF properties
bool test_python_to_cpp()
{
	std::cout << "\n=== Test 1: Python → C++ (Load Python binary in C++) ===\n";

	// Load keys from CSV
	auto keys = load_keys_from_csv("test_data_py.csv");
	if (keys.empty())
	{
		std::cerr << "✗ Failed to load keys from CSV\n";
		return false;
	}
	std::cout << "✓ Loaded " << keys.size() << " test keys\n";

	// Load MPHF from Python binary
	std::ifstream is("test_data_py.mphf", std::ios::binary);
	if (!is)
	{
		std::cerr << "✗ Failed to open Python binary file\n";
		return false;
	}

	boophf_t bphf;
	bphf.load(is);
	is.close();
	std::cout << "✓ Loaded MPHF from Python binary\n";

	// Verify MPHF properties:
	// 1. All keys can be looked up
	// 2. All hash values are in range [0, n-1]
	// 3. All hash values are unique (perfect hash)
	std::cout << "Verifying MPHF properties...\n";

	std::vector<uint64_t> hash_values;
	hash_values.reserve(keys.size());
	int lookup_errors = 0;
	int out_of_range = 0;

	for (uint64_t key : keys)
	{
		uint64_t hash_val = bphf.lookup(key);

		// Check if lookup succeeded (BBHash returns values in [0, n-1])
		if (hash_val >= keys.size())
		{
			std::cerr << "✗ Out of range for key " << key << ": " << hash_val
			          << " not in [0, " << keys.size() - 1 << "]\n";
			out_of_range++;
			if (out_of_range >= 10)
			{
				std::cerr << "  (stopping after 10 errors)\n";
				break;
			}
		}
		else
		{
			hash_values.push_back(hash_val);
		}
	}

	if (out_of_range > 0)
	{
		std::cerr << "✗ MPHF verification failed with " << out_of_range
		          << " out-of-range values\n";
		return false;
	}

	// Check for uniqueness (no collisions)
	std::sort(hash_values.begin(), hash_values.end());
	auto unique_end = std::unique(hash_values.begin(), hash_values.end());
	size_t unique_count = std::distance(hash_values.begin(), unique_end);

	if (unique_count != hash_values.size())
	{
		std::cerr << "✗ Hash collision detected!\n";
		std::cerr << "  Expected " << hash_values.size() << " unique hashes, got "
		          << unique_count << "\n";
		return false;
	}

	std::cout << "✓ All " << keys.size() << " keys can be looked up\n";
	std::cout << "✓ All hash values in valid range [0, " << keys.size() - 1 << "]\n";
	std::cout << "✓ All hash values are unique (perfect hash)\n";
	return true;
}

// Test 2: Build MPHF in C++, save, load in C++, then save for Python to load
bool test_cpp_to_python()
{
	std::cout << "\n=== Test 2: C++ → Python (C++ export for Python) ===\n";

	// Use same keys as Python for consistency
	std::vector<uint64_t> keys;
	for (uint64_t i = 1000; i < 2000; ++i)
	{
		keys.push_back(i);
	}
	std::cout << "✓ Generated " << keys.size() << " test keys\n";

	// Build MPHF
	boophf_t bphf(keys.size(), keys, 1, 2.0, false, false);
	std::cout << "✓ Built MPHF in C++\n";

	// Save to binary file
	std::ofstream os("test_data_cpp.mphf", std::ios::binary);
	if (!os)
	{
		std::cerr << "✗ Failed to create output file\n";
		return false;
	}
	bphf.save(os);
	os.close();
	std::cout << "✓ Saved MPHF to binary file\n";

	// Save expected results to CSV for Python to verify
	std::ofstream csv("test_data_cpp.csv");
	if (!csv)
	{
		std::cerr << "✗ Failed to create CSV file\n";
		return false;
	}
	csv << "key,hash_value\n";
	for (uint64_t key : keys)
	{
		uint64_t hash_val = bphf.lookup(key);
		csv << key << "," << hash_val << "\n";
	}
	csv.close();
	std::cout << "✓ Saved expected results to CSV\n";

	// Verify by loading again in C++
	std::ifstream is("test_data_cpp.mphf", std::ios::binary);
	if (!is)
	{
		std::cerr << "✗ Failed to open saved file for verification\n";
		return false;
	}

	boophf_t bphf_loaded;
	bphf_loaded.load(is);
	is.close();

	// Verify a few keys
	bool all_match = true;
	size_t num_to_check = keys.size() < 10 ? keys.size() : 10;
	for (size_t i = 0; i < num_to_check; ++i)
	{
		uint64_t key = keys[i];
		uint64_t original_val = bphf.lookup(key);
		uint64_t loaded_val = bphf_loaded.lookup(key);
		if (original_val != loaded_val)
		{
			std::cerr << "✗ C++ save/load mismatch for key " << key << "\n";
			all_match = false;
		}
	}

	if (all_match)
	{
		std::cout << "✓ C++ save/load verification passed\n";
		return true;
	}
	else
	{
		std::cerr << "✗ C++ save/load verification failed\n";
		return false;
	}
}

int main()
{
	std::cout << "==================================\n";
	std::cout << "Cross-Language Binary Format Tests\n";
	std::cout << "==================================\n";

	bool test1_passed = test_python_to_cpp();
	bool test2_passed = test_cpp_to_python();

	std::cout << "\n==================================\n";
	std::cout << "Test Results:\n";
	std::cout << "==================================\n";
	std::cout << "Test 1 (Python→C++): " << (test1_passed ? "✓ PASSED" : "✗ FAILED") << "\n";
	std::cout << "Test 2 (C++→Python): " << (test2_passed ? "✓ PASSED" : "✗ FAILED") << "\n";

	if (test1_passed && test2_passed)
	{
		std::cout << "\n✓ All cross-language tests passed!\n";
		return 0;
	}
	else
	{
		std::cout << "\n✗ Some tests failed.\n";
		return 1;
	}
}
