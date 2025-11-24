# 跨语言二进制兼容性测试 - 重要说明

## 关键理解

### ❌ 错误的理解
"C++ 和 Python 对同一键应该产生相同的哈希值"

### ✅ 正确的理解
"C++ 和 Python 的二进制格式兼容，可以互相加载，每个实现都能正确处理其加载的 MPHF"

## 为什么哈希值可以不同？

最小完美哈希函数（MPHF）**只保证**：
1. 每个键映射到唯一的整数
2. 整数在 [0, n-1] 范围内
3. 没有碰撞（完美哈希）

MPHF **不保证**：
- 不同实现对同一键产生相同的哈希值
- 哈希值的顺序或分布

### 类比
就像两个人用不同的方法给同一组物品编号：
- 人 A: 按大小排序后编号 1, 2, 3...
- 人 B: 按颜色分组后编号 1, 2, 3...

两种方法都是**正确的编号方案**，但**编号结果不同**。

## 测试策略

### Test 1: Python → C++ ✅
1. Python 构建 MPHF 并保存
2. C++ 加载该 MPHF
3. C++ 验证：
   - 所有键都能查询
   - 所有哈希值在 [0, n-1]
   - 所有哈希值唯一（无碰撞）

### Test 2: C++ → Python ✅
1. C++ 构建 MPHF 并保存
2. Python 加载该 MPHF
3. Python 验证：
   - 所有键都能查询
   - 所有哈希值在 [0, n-1]
   - 所有哈希值唯一（无碰撞）

## 二进制格式兼容性

测试验证的是**格式兼容性**，不是**值兼容性**：

✅ **验证内容**：
- Header 格式正确（gamma, nb_levels, nelem, lastbitsetrank）
- Bitset 结构正确（size, nchar, bitArray, ranks）
- Final hash table 格式正确（size, key-value pairs）
- 字节序正确（little-endian）
- 数据类型大小正确（uint64_t = 8 bytes, etc.）

❌ **不验证内容**：
- 具体的哈希值
- 键到哈希值的映射关系
- 内部数据结构的具体内容

## 实际应用场景

### 场景 1：Python 构建，C++ 使用
```python
# Python 端
keys = [1000, 1001, 1002, ...]
mph = mphf(n=len(keys), input_range=keys)
mph.save("index.mphf")

# 同时保存键列表
with open("keys.txt", "w") as f:
    for key in keys:
        f.write(f"{key}\n")
```

```cpp
// C++ 端
boophf_t mph;
std::ifstream is("index.mphf", std::ios::binary);
mph.load(is);

// 读取键列表
std::vector<uint64_t> keys = load_keys("keys.txt");

// 使用相同的键查询
for (auto key : keys) {
    uint64_t hash = mph.lookup(key);  // 正确工作
    // 使用 hash 作为索引访问数据
}
```

### 场景 2：C++ 构建，Python 使用
```cpp
// C++ 端
std::vector<uint64_t> keys = {...};
boophf_t mph(keys.size(), keys, 1, 2.0, false);
std::ofstream os("index.mphf", std::ios::binary);
mph.save(os);

// 保存键列表
save_keys("keys.txt", keys);
```

```python
# Python 端
mph = mphf.load("index.mphf")

# 读取键列表
keys = load_keys("keys.txt")

# 使用相同的键查询
for key in keys:
    hash = mph.lookup(key)  # 正确工作
    # 使用 hash 作为索引访问数据
```

## 关键点

### ✅ 保证的兼容性
1. **格式兼容**：二进制文件可以互相读取
2. **功能正确**：加载后的 MPHF 对原始键集合正常工作
3. **属性保持**：元数据（gamma, nelem 等）正确保存和加载

### ❌ 不保证的内容
1. **值一致性**：不同实现的哈希值可能不同
2. **实现细节**：内部算法可能有差异
3. **性能特性**：构建和查询速度可能不同

## 测试更新

### 更新前（错误）
```cpp
// 比较具体的哈希值
uint64_t expected_hash = csv_data[key];
uint64_t actual_hash = mph.lookup(key);
if (expected_hash != actual_hash) {
    // 报错 ❌
}
```

### 更新后（正确）
```cpp
// 验证 MPHF 属性
std::vector<uint64_t> hashes;
for (auto key : keys) {
    uint64_t hash = mph.lookup(key);
    // 1. 检查范围
    if (hash >= keys.size()) { /* 报错 */ }
    hashes.push_back(hash);
}
// 2. 检查唯一性
if (has_duplicates(hashes)) { /* 报错 */ }
// ✅ 通过！
```

## 总结

跨语言二进制兼容性测试的核心是：

**不是验证"同一键产生同一值"，而是验证"格式可以互换，功能正确运行"。**

这就像：
- 两个不同的压缩程序（zip, rar）
- 可以读取彼此的文件格式 ✅
- 但解压后的文件顺序可能不同 ✅
- 只要最终文件内容正确就行 ✅

类似地：
- C++ 和 Python 可以读取彼此的 MPHF 文件 ✅
- 但对同一键的哈希值可能不同 ✅
- 只要 MPHF 属性正确（唯一、范围内）就行 ✅
