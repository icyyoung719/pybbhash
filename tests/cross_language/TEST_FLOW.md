# 跨语言测试流程说明

## 📋 测试流程

### 整体架构

```
测试样本 → Python/C++ 分别处理 → 二进制互导 → 观察哈希差异
```

### 详细步骤

#### 1. 生成测试样本（固定种子）
```bash
python generate_test_keys.py
```
- 使用固定随机种子（42）生成 1000 个测试键
- 输出：`test_keys.csv`（单列，只有键）

#### 2. Python 处理
```bash
python export_test_data.py
```
- 读取 `test_keys.csv`
- 构建 Python MPHF（gamma=2.0）
- 输出：
  - `test_data_py.mphf` - 二进制文件
  - `test_data_py_hashes.csv` - 哈希结果（key, hash_value）

#### 3. C++ 处理
```bash
g++ -std=c++17 test_compatibility.cpp -o test_compatibility -I. -I./cpp_headers
./test_compatibility
```
- 读取 `test_keys.csv`
- 构建 C++ MPHF（gamma=2.0）
- 输出：
  - `test_data_cpp.mphf` - 二进制文件
  - `test_data_cpp_hashes.csv` - 哈希结果（key, hash_value）
- 同时加载 Python 的二进制并验证
- 比较 Python 和 C++ 的哈希值

#### 4. Python 验证 C++ 二进制
```bash
python verify_cpp_export.py
```
- 加载 C++ 的二进制文件
- 验证二进制兼容性
- 可选：比较与 C++ 哈希值的差异

## 🎯 测试验证内容

### 二进制兼容性（必须通过）
- ✅ Python 能加载 C++ 导出的二进制
- ✅ C++ 能加载 Python 导出的二进制
- ✅ 所有键都能成功查询
- ✅ 所有哈希值在有效范围 [0, n-1]
- ✅ 所有哈希值唯一（无碰撞）

### 哈希值比较（观察性质）
- 📊 统计 Python 和 C++ 哈希值的匹配率
- 📊 展示示例差异
- ⚠️ **不要求完全一致**，允许差异

## 🔍 为什么哈希值可以不同？

MPHF 的目标是：
1. 将 n 个键映射到 [0, n-1] 的整数
2. 保证无碰撞（完美哈希）

**不要求：**
- 不同实现对同一键产生相同的哈希值
- 构建过程的中间状态一致

**兼容性体现在：**
- 二进制格式能互相读取
- 读取后能正确查询所有键
- MPHF 性质得到保持

## 📁 生成的文件

### 输入
- `test_keys.csv` - 测试样本（固定种子生成）

### Python 输出
- `test_data_py.mphf` - Python MPHF 二进制
- `test_data_py_hashes.csv` - Python 哈希结果

### C++ 输出
- `test_data_cpp.mphf` - C++ MPHF 二进制
- `test_data_cpp_hashes.csv` - C++ 哈希结果

## 🚀 一键运行

```bash
cd tests/cross_language
python run_tests.py
```

这会自动执行所有步骤：
1. 生成测试键
2. Python 构建和导出
3. 编译 C++ 程序
4. C++ 构建、加载 Python 二进制、比较哈希
5. Python 加载 C++ 二进制

## ✅ 成功标准

所有步骤通过，输出类似：
```
Tests passed: 5/5

✓ ALL TESTS PASSED!

Key findings:
  1. Binary format is fully compatible between Python and C++
  2. Both implementations can load each other's MPHF files
  3. All keys can be looked up successfully
  4. Hash value differences (if any) are expected and acceptable
```

## 🔬 观察哈希差异

测试会输出类似：
```
Comparison Summary:
  Total keys:   1000
  Matches:      0 (0%)
  Mismatches:   1000 (100%)

✓ Different hash values (expected for independent MPHF builds)
  Both implementations produce valid MPHFs with different assignments.
```

这是**正常且符合预期的**！重要的是：
- 二进制格式兼容 ✅
- 所有键能查询 ✅
- 无碰撞 ✅
- 哈希值范围正确 ✅
